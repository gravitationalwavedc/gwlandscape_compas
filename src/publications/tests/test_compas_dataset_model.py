import pathlib
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import testcases, override_settings

from publications.models import Upload, CompasPublication, CompasModel, CompasDatasetModel


class TestCompasDatasetModel(testcases.TestCase):
    def setUp(self):
        self.model = CompasModel.create_model('test', 'summary', 'description')

        self.publication = CompasPublication.create_publication(
            author='test author',
            title='test title',
            arxiv_id='test arxiv_id'
        )

        self.test_job_archive = SimpleUploadedFile(
            name='test.tar.gz',
            content=open('./publications/tests/test_data/test_job.tar.gz', 'rb').read(),
            content_type='application/gzip'
        )

        self.test_job_single = SimpleUploadedFile(
            name='COMPAS_Output.h5',
            content=open('./publications/tests/test_data/test_job/COMPAS_Output/COMPAS_Output.h5', 'rb').read(),
            content_type='application/x-bag'
        )

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_create(self):
        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        self.assertEqual(CompasDatasetModel.objects.all().count(), 1)
        self.assertEqual(CompasDatasetModel.objects.last().compas_publication, self.publication)
        self.assertEqual(CompasDatasetModel.objects.last().compas_model, self.model)

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_delete(self):
        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        file = model.upload_set.first().file.path
        self.assertTrue(pathlib.Path(file).exists())

        CompasDatasetModel.delete_dataset_model(model.id)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 0)
        self.assertEqual(Upload.objects.all().count(), 0)

        # The Uploaded files should be deleted
        self.assertFalse(pathlib.Path(file).exists())

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_str(self):
        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        self.assertEqual(str(model), "test title - test")

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_save_no_file(self):
        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            None
        )

        self.assertEqual(Upload.objects.all().count(), 0)

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_save_archive(self):
        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        self.assertEqual(Upload.objects.all().count(), 5)

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_save_single_file(self):
        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_single
        )

        self.assertEqual(Upload.objects.all().count(), 1)
        self.assertEqual(Upload.objects.last().file.name, 'publications/1/1/COMPAS_Output.h5')
