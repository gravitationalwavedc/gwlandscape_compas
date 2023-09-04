from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from compasui.tests.testcases import CompasTestCase
from publications.models import FileDownloadToken, CompasModel, CompasPublication, CompasDatasetModel


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestFileDownloadToken(CompasTestCase):
    def setUp(self):
        self.model = CompasModel.create_model('test', 'summary', 'description')

        self.publication = CompasPublication.create_publication(
            author='test author',
            title='test title',
            arxiv_id='test arxiv_id'
        )

        self.placeholder_dataset = SimpleUploadedFile(
            name='COMPAS_Output.h5',
            content=open('./publications/tests/test_data/test_job/COMPAS_Output/COMPAS_Output.h5', 'rb').read(),
            content_type='application/x-bag'
        )

        self.dataset = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.placeholder_dataset
        )

    def test_create(self):
        # Test that given a dataset, and a list of paths, the correct objects are created in the database
        # and the correct order of objects is returned

        paths = [
            "/awesome_path1/data.txt",
            "/awesome_path1/data1.txt",
            "/awesome_path1/data2.txt",
            "/awesome_path1/data3.txt",
            "/awesome_path/data.txt",
        ]

        before = timezone.now()
        result = FileDownloadToken.create(self.dataset, paths)
        after = timezone.now()

        for i, p in enumerate(paths):
            self.assertEqual(result[i].path, p)
            self.assertEqual(result[i].dataset, self.dataset)
            self.assertTrue(result[i].token)
            self.assertTrue(before < result[i].created < after)

        for p in paths:
            result = FileDownloadToken.objects.get(dataset=self.dataset, path=p)
            self.assertEqual(result.path, p)
            self.assertEqual(result.dataset, self.dataset)
            self.assertTrue(result.token)
            self.assertTrue(before < result.created < after)

    def test_prune(self):
        # Test that FileDownloadToken objects older than settings.FILE_DOWNLOAD_TOKEN_EXPIRY are correctly removed from
        # the database

        # Test that objects created now are not removed
        paths = [
            "/awesome_path1/data.txt",
            "/awesome_path1/data1.txt",
            "/awesome_path1/data2.txt",
            "/awesome_path1/data3.txt",
            "/awesome_path/data.txt",
        ]

        FileDownloadToken.create(self.dataset, paths)
        after = timezone.now()

        FileDownloadToken.prune()

        self.assertEqual(FileDownloadToken.objects.all().count(), 5)

        # Check objects just inside the deletion time are not deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY - 1)
            r.save()

        FileDownloadToken.prune()

        self.assertEqual(FileDownloadToken.objects.all().count(), 5)

        # Check objects just outside the deletion time are deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1)
            r.save()

        FileDownloadToken.prune()

        self.assertEqual(FileDownloadToken.objects.all().count(), 0)

    def test_get_paths(self):
        # Test that getting paths with valid tokens returns a list of paths in order
        paths = [
            "/awesome_path1/data.txt",
            "/awesome_path1/data1.txt",
            "/awesome_path1/data2.txt",
            "/awesome_path1/data3.txt",
            "/awesome_path/data.txt",
        ]

        fd_tokens = FileDownloadToken.create(self.dataset, paths)
        after = timezone.now()

        tokens = [tk.token for tk in fd_tokens]
        result = FileDownloadToken.get_paths(self.dataset, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Check reverse order
        fd_tokens.reverse()
        tokens = [tk.token for tk in fd_tokens]
        result = FileDownloadToken.get_paths(self.dataset, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Check that prune works as expected
        # Check objects just inside the deletion time are not deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY - 1)
            r.save()

        result = FileDownloadToken.get_paths(self.dataset, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Set one object outside the expiry window
        r = FileDownloadToken.objects.all()[2]
        r.created = after - timezone.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1)
        r.save()

        result = FileDownloadToken.get_paths(self.dataset, tokens)

        for i, tk in enumerate(fd_tokens):
            if i == 2:
                self.assertEqual(result[i], None)
            else:
                self.assertEqual(result[i], tk.path)

        # Check objects just outside the deletion time are deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1)
            r.save()

        result = FileDownloadToken.get_paths(self.dataset, tokens)
        self.assertEqual(result, [None] * 5)

        # No records should exist in the database anymore
        self.assertFalse(FileDownloadToken.objects.all().exists())
