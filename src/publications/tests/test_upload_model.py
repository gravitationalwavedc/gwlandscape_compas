from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import testcases, override_settings

from publications.models import Upload, CompasPublication, CompasModel, CompasDatasetModel


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestUploadModel(testcases.TestCase):
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

        self.dataset_model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

    def test_create(self):
        # Create is triggered when we initiate the creation of CompasDatasetModel in setUp()
        files = [
            'COMPAS_Output.h5',
            'Run_Details',
            'BSE_grid.txt'
        ]

        self.assertEqual(3, Upload.objects.all().count())
        for f in files:
            self.assertTrue(Upload.objects.filter(file__contains=f, dataset_model=self.dataset_model).exists())

    def test_str(self):
        upload = Upload.objects.get(file__contains='COMPAS_Output.h5', dataset_model=self.dataset_model)
        self.assertEqual(str(upload), 'COMPAS_Output.h5')
