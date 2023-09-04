import datetime
import os
import tarfile
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from publications.utils.misc import check_publication_management_user


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

    @classmethod
    def update_keyword(cls, _id, tag=None):
        keyword = cls.objects.get(id=_id)
        if tag is not None:
            keyword.tag = tag
        keyword.save()

    @classmethod
    def filter_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)


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
        keywords = Keyword.filter_by_ids(kwargs.pop('keywords', []))

        result = cls.objects.create(**kwargs)
        result.keywords.set(keywords)

        return result

    @classmethod
    def delete_publication(cls, _id):
        cls.objects.get(id=_id).delete()

    @classmethod
    def update_publication(cls, _id, **kwargs):
        publication = cls.objects.get(id=_id)
        keyword_ids = kwargs.pop('keywords', None)
        if keyword_ids is not None:
            keywords = Keyword.filter_by_ids(keyword_ids)
            publication.keywords.set(keywords)

        for key, val in kwargs.items():
            setattr(publication, key, val)
        publication.save()

    @classmethod
    def public_filter(cls, queryset, info):
        if not check_publication_management_user(info.context.user):
            return queryset.exclude(public=False)
        else:
            return queryset


class CompasModel(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=50, null=False, blank=False)
    summary = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_model(cls, name, summary=None, description=None):
        return cls.objects.create(
            name=name,
            summary=summary,
            description=description
        )

    @classmethod
    def delete_model(cls, _id):
        cls.objects.get(id=_id).delete()

    @classmethod
    def update_model(cls, _id, **kwargs):
        model = cls.objects.get(id=_id)
        for key, val in kwargs.items():
            setattr(model, key, val)
        model.save()


class CompasDatasetModel(models.Model):
    compas_publication = models.ForeignKey(CompasPublication, models.CASCADE, related_name='dataset_models')
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
        # Clean up any related Upload files
        obj = cls.objects.get(id=_id)
        for file in obj.upload_set.all():
            file.file.delete()

        # Clean up the original uploaded file
        cls.objects.get(id=_id).file.delete()
        cls.objects.get(id=_id).delete()

    @classmethod
    def update_dataset_model(cls, _id, compas_publication=None, compas_model=None):
        dataset_model = cls.objects.get(id=_id)
        if compas_publication:
            dataset_model.compas_publication = compas_publication
        if compas_model:
            dataset_model.compas_model = compas_model
        dataset_model.save()

    def __str__(self):
        return f"{self.compas_publication.title} - {self.compas_model.name}"

    def save(self, *args, **kwargs):
        """
        overwrites default save behavior
        """
        # Validate uploaded file has one and only one h5 file
        # Can't check with is_tarfile because it requires a path, and the file hasn't been written to disk yet
        if self.file.name:
            try:
                with tarfile.open(fileobj=self.file) as f:
                    if sum(Path(name).suffix == '.h5' for name in f.getnames()) != 1:
                        raise ValidationError('Dataset must have exactly one assigned h5 file')
            except tarfile.ReadError:
                if Path(self.file.name).suffix != '.h5':
                    raise ValidationError('Uploaded dataset should be a .h5 file')

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

        for member in dataset_tar.getmembers():
            # ignore any directory but include its contents
            if not member.isdir():
                # extract files into dataset directory
                # (this will create subdirectories as well, exactly as in the tarball)
                dataset_tar.extract(member, dataset_dir)
                Upload.create_upload(os.path.join(os.path.dirname(self.file.name), member.name), self)

        dataset_tar.close()
        # remove the tar file after decompression
        self.file.delete()

    def get_data_file(self):
        return self.upload_set.get(file__iendswith=".h5").file


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


class CompasDatasetModelUploadToken(models.Model):
    """
    This model tracks file upload tokens that can be used to upload compas dataset model files rather than using
    traditional JWT authentication
    """
    # The job upload token
    token = models.UUIDField(unique=True, default=uuid.uuid4, db_index=True)
    # The ID of the user the upload token was created for (Used to provide the user of the uploaded job)
    user_id = models.IntegerField()
    # When the token was created
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def get_by_token(cls, token):
        """
        Returns the instance matching the specified token, or None if expired or not found
        """
        # First prune any old tokens which may have expired
        cls.prune()

        # Next try to find the instance matching the specified token
        inst = cls.objects.filter(token=token)
        if not inst.exists():
            return None

        return inst.first()

    @classmethod
    def create(cls, user):
        """
        Creates a CompasDatasetModelUploadToken object
        """
        # First prune any old tokens which may have expired
        cls.prune()

        # Next create and return a new token instance
        return cls.objects.create(user_id=user.user_id)

    @classmethod
    def prune(cls):
        """
        Removes any expired tokens from the database
        """
        cls.objects.filter(
            created__lt=timezone.now() - datetime.timedelta(seconds=settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY)
        ).delete()


class FileDownloadToken(models.Model):
    """
    This model tracks files uploaded as part of a dataset, allowing them to be downloaded
    """
    dataset = models.ForeignKey(CompasDatasetModel, on_delete=models.CASCADE, db_index=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4, db_index=True)
    path = models.TextField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def prune(cls):
        """
        Removes expired tokens from the database
        :return:
        """
        cls.objects.filter(
            created__lt=timezone.now() - datetime.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY)
        ).delete()

    @classmethod
    def get_by_token(cls, token):
        cls.prune()
        tok = cls.objects.filter(token=token)
        if not tok.exists():
            return None
        return tok.first()

    @classmethod
    def create(cls, dataset, paths):
        """
        Creates a bulk number of FileDownloadToken objects for a specific dataset and list of paths, and returns the
        created objects
        """
        data = [cls(dataset=dataset, path=p) for p in paths]
        return cls.objects.bulk_create(data)

    @classmethod
    def get_paths(cls, dataset, tokens):
        """
        Returns a list of paths from a list of tokens, any token that isn't found will have a path of None
        The resulting list, will have identical size and ordering to the provided list of tokens
        """
        cls.prune()
        objects = {
            str(f.token): f.path for f in cls.objects.filter(dataset=dataset, token__in=tokens)
        }
        return [
            objects[str(tok)] if str(tok) in objects else None for tok in tokens
        ]
