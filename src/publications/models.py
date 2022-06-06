import os
import tarfile

from django.db import models
from graphql_relay import from_global_id

from publications.utils import check_publication_management_user


class Keyword(models.Model):
    class Meta:
        ordering = ['tag']

    tag = models.CharField(max_length=255, blank=False, null=False, unique=True)

    def __str__(self):
        return self.tag

    @classmethod
    def create_keyword(cls, tag):
        return cls.objects.create(
            tag=tag
        )

    @classmethod
    def delete_keyword(cls, _id):
        cls.objects.get(id=_id).delete()


def job_directory_path(instance, filename):
    """
    a callable to generate a custom directory path to upload file to
    instance: an instance of the model to which the file belongs
    filename: name of the file to be uploaded
    """
    # change file name if it has spaces
    fname = filename.replace(" ", "_")
    dataset_id = str(instance.compas_publication.id)
    model_id = str(instance.compas_model.id)
    # dataset files will be saved in MEDIA_ROOT/publications/dataset_id/model_id/
    return os.path.join("publications", dataset_id, model_id, fname)


class CompasPublication(models.Model):
    class Meta:
        ordering = ['title']

    author = models.CharField(max_length=255, blank=False, null=False)
    # published defines if the job was published in a journal/arxiv
    published = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    year = models.IntegerField(null=True)
    journal = models.CharField(max_length=255, null=True)
    journal_doi = models.CharField(max_length=255, null=True)
    dataset_doi = models.CharField(max_length=255, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    # public defines if the job is publicly accessible
    public = models.BooleanField(default=False)
    download_link = models.TextField(blank=True, null=True)
    arxiv_id = models.CharField(max_length=255, blank=False)
    keywords = models.ManyToManyField(Keyword)

    def __str__(self):
        return self.title

    @classmethod
    def filter_by_keyword(cls, keyword=None):
        return cls.objects.all().filter(keywords__tag=keyword) if keyword else cls.objects.all()

    @classmethod
    def create_publication(cls, **kwargs):
        if keyword_ids := kwargs.get('keywords', []):
            del kwargs['keywords']

        result = cls.objects.create(**kwargs)

        [result.keywords.add(Keyword.objects.get(id=from_global_id(_id)[1])) for _id in keyword_ids]

        return result

    @classmethod
    def delete_publication(cls, _id):
        cls.objects.get(id=_id).delete()

    @classmethod
    def public_filter(cls, queryset, info):
        if not check_publication_management_user(info.context.user):
            return queryset.exclude(public=False)
        else:
            return queryset


class CompasModel(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=50, null=True, blank=True)
    summary = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_model(cls, name, summary, description):
        return cls.objects.create(
            name=name,
            summary=summary,
            description=description
        )

    @classmethod
    def delete_model(cls, _id):
        cls.objects.get(id=_id).delete()


class CompasDatasetModel(models.Model):
    compas_publication = models.ForeignKey(CompasPublication, models.CASCADE)
    compas_model = models.ForeignKey(CompasModel, models.CASCADE)
    file = models.FileField(upload_to=job_directory_path, blank=True, null=True)

    @classmethod
    def create_dataset_model(cls, compas_publication, compas_model, file):
        return cls.objects.create(
            compas_publication=compas_publication,
            compas_model=compas_model,
            file=file
        )

    @classmethod
    def delete_dataset_model(cls, _id):
        cls.objects.get(id=_id).delete()

    def __str__(self):
        return f"{self.compas_publication.title} - {self.compas_model.name}"

    def save(self, *args, **kwargs):
        """
        overwrites default save behavior
        """
        super().save(*args, **kwargs)
        # Check file name is not empty after saving the model and uploading file
        if self.file.name:
            # Check the uploaded file could be decompressed using tarfile
            if tarfile.is_tarfile(self.file.path):
                self.decompress_tar_file()
            # If the uploaded file is an individual file
            else:
                Upload.create_upload(self.file.name, self)

    def decompress_tar_file(self):
        # Get the actual path for uploaded file
        dataset_dir = os.path.dirname(self.file.path)
        dataset_tar = tarfile.open(self.file.path)
        # dataset_tar.extractall(dataset_dir)
        for member in dataset_tar.getmembers():
            # ignore any directory but include its contents
            if not member.isdir():
                # extract files into dataset directory
                # (this will create subdirectories as well, exactly as in the tarball)
                dataset_tar.extract(member, dataset_dir)
                Upload.create_upload(os.path.join(os.path.dirname(self.file.name), member.name), self)

        dataset_tar.close()
        # remove the tar file after decompression
        os.remove(self.file.path)


class Upload(models.Model):
    file = models.FileField(blank=True, null=True)
    dataset_model = models.ForeignKey(CompasDatasetModel, models.CASCADE)

    # create an Upload model for an uploaded file
    @classmethod
    def create_upload(cls, filepath, dataset_model):
        """
        filepath is the relative path of the uploaded file within MEDIA_ROOT
        """
        upload = Upload()
        upload.file = filepath
        upload.dataset_model = dataset_model
        upload.save()

    def __str__(self):
        return os.path.basename(self.file.name)
