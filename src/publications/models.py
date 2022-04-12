import os
import tarfile

import h5py
from django.db import models
from graphql_relay import from_global_id


class Keyword(models.Model):
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
    def all(cls):
        return cls.objects.all().order_by('tag')


def job_directory_path(instance, filename):
    """
    a callable to generate a custom directory path to upload file to
    instance: an instance of the model to which the file belongs
    filename: name of the file to be uploaded
    """
    # change file name if it has spaces
    fname = filename.replace(" ", "_")
    dataset_id = str(instance.compasjob.id)
    model_id = str(instance.compasmodel.id)
    # dataset files will be saved in MEDIA_ROOT/datasets/dataset_id/model_id/
    return os.path.join("datasets", dataset_id, model_id, fname)


class CompasPublication(models.Model):
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


class CompasModel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    summary = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CompasDatasetModel(models.Model):
    compas_publication = models.ForeignKey(CompasPublication, models.CASCADE)
    compas_model = models.ForeignKey(CompasModel, models.CASCADE)
    files = models.FileField(upload_to=job_directory_path, blank=True, null=True)

    def __str__(self):
        return f"{self.compas_publication.title} - {self.compas_model.name}"

    def save(self, *args, **kwargs):
        """
        overwrites default save behavior
        """
        super().save(*args, **kwargs)
        # Check file name is not empty after saving the model and uploading file
        if self.files.name:
            # Check the uploaded file could be decompressed using tarfile
            if tarfile.is_tarfile(self.files.path):
                self.decompress_tar_file()
            # If the uploaded file is an individual file
            else:
                self.create_upload(self.files.name)

    def decompress_tar_file(self):
        # Get the actual path for uploaded file
        dataset_dir = os.path.dirname(self.files.path)
        dataset_tar = tarfile.open(self.files.path)
        # dataset_tar.extractall(dataset_dir)
        for member in dataset_tar.getmembers():
            # ignore any directory but include its contents
            if not member.isdir():
                # extract files into dataset directory
                # (this will create subdirectories as well, exactly as in the tarball)
                dataset_tar.extract(member, dataset_dir)
                self.create_upload(os.path.join(os.path.dirname(self.files.name), member.name))
        dataset_tar.close()
        # remove the tar file after decompression
        os.remove(self.files.path)

    # create an Upload model for an uploaded file
    def create_upload(self, filepath):
        """
        filepath is the relative path of the uploaded file within MEDIA_ROOT
        """
        upload = Upload()
        upload.file = filepath
        upload.dataset_model = self
        upload.save()

    def get_run_details(self):
        """
        query file: "run_details.txt"
        """
        return self.upload_set.filter(file__iendswith="Run_Details.txt")

    def get_data(self):
        """
        query file: "*.h5"
        """
        return self.upload_set.filter(file__iendswith=".h5")


class Upload(models.Model):
    file = models.FileField(blank=True, null=True)
    dataset_model = models.ForeignKey(CompasDatasetModel, models.CASCADE)

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_content(self):
        """
        get the content of a file; will be called only on txt files
        """
        if self.file.storage.exists(self.file.name):

            with self.file.open("r") as f:
                return f.read()
        else:
            return "File not found"

    def read_stats(self):
        """
        read data length in h5 file
        """
        data_stats = {}

        if self.file.storage.exists(self.file.name):
            data = h5py.File(self.file, "r")
            for key in data.keys():
                prim_key = list(data[key])[0]
                stat = len(data[key][prim_key])
                data_stats[key] = stat

        return data_stats
