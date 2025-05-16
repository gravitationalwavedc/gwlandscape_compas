from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from unittest.mock import Mock

from compasui.models import (
    CompasJob,
    BasicParameter,
    AdvancedParameter,
    FileDownloadToken,
)


class TestCompasJobModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job = CompasJob.objects.create(
            user_id=1,
            name="Test Job",
            description="Test job description",
            private=False,
        )
        cls.job.save()

    def test_get_job_by_name_exists(self):
        mock_user = Mock()
        mock_user.user_id = 1
        job = CompasJob.get_by_name(name=self.job.name, user=mock_user)
        self.assertIsNotNone(job)

    def test_get_job_by_name_not_found(self):
        mock_user = Mock()
        mock_user.user_id = 1
        job = CompasJob.get_by_name(name="another name", user=mock_user)
        self.assertIsNone(job)


class TestModels(TestCase):
    def test_job_to_json(self):
        """
        Check that a job object can be successfully converted to json
        """

        job = CompasJob(
            user_id=1, name="first job", description="first job description"
        )
        job.save()

        first = BasicParameter(job=job, name="first_parameter", value="1.0")
        first.save()

        second = BasicParameter(job=job, name="second_parameter", value="2.0")
        second.save()

        advanced = AdvancedParameter(job=job, name="advanced_parameter1", value="0.001")
        advanced.save()

        self.assertDictEqual(
            job.as_json(),
            {
                "name": "first job",
                "description": "first job description",
                "basic": {"first_parameter": "1.0", "second_parameter": "2.0"},
                "advanced": {"advanced_parameter1": "0.001"},
            },
        )


class TestFileDownloadToken(TestCase):
    """
    Copied from GWLab
    """

    @classmethod
    def setUpTestData(cls):
        cls.job = CompasJob.objects.create(
            user_id=1,
            name="Test Job",
            description="Test job description",
            private=False,
        )
        cls.job.save()

    def test_create(self):
        # Test that given a job, and a list of paths, the correct objects are created in the database
        # and the correct order of objects is returned

        paths = ["/path1/data.txt", "/path1/data1.txt", "/path2/data.txt"]

        before = timezone.now()
        result = FileDownloadToken.create(self.job, paths)
        after = timezone.now()

        for i, p in enumerate(paths):
            self.assertEqual(result[i].path, p)
            self.assertEqual(result[i].job, self.job)
            self.assertTrue(result[i].token)
            self.assertTrue(before < result[i].created < after)

        for p in paths:
            result = FileDownloadToken.objects.get(job=self.job, path=p)
            self.assertEqual(result.path, p)
            self.assertEqual(result.job, self.job)
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

        FileDownloadToken.create(self.job, paths)
        after = timezone.now()

        FileDownloadToken.prune()

        self.assertEqual(FileDownloadToken.objects.all().count(), 5)

        # Check objects just inside the deletion time are not deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(
                seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY - 1
            )
            r.save()

        FileDownloadToken.prune()

        self.assertEqual(FileDownloadToken.objects.all().count(), 5)

        # Check objects just outside the deletion time are deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(
                seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1
            )
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

        fd_tokens = FileDownloadToken.create(self.job, paths)
        after = timezone.now()

        tokens = [tk.token for tk in fd_tokens]
        result = FileDownloadToken.get_paths(self.job, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Check reverse order
        fd_tokens.reverse()
        tokens = [tk.token for tk in fd_tokens]
        result = FileDownloadToken.get_paths(self.job, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Check that prune works as expected
        # Check objects just inside the deletion time are not deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(
                seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY - 1
            )
            r.save()

        result = FileDownloadToken.get_paths(self.job, tokens)

        for i, tk in enumerate(fd_tokens):
            self.assertEqual(result[i], tk.path)

        # Set one object outside the expiry window
        r = FileDownloadToken.objects.all()[2]
        r.created = after - timezone.timedelta(
            seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1
        )
        r.save()

        result = FileDownloadToken.get_paths(self.job, tokens)

        for i, tk in enumerate(fd_tokens):
            if i == 2:
                self.assertEqual(result[i], None)
            else:
                self.assertEqual(result[i], tk.path)

        # Check objects just outside the deletion time are deleted
        for r in FileDownloadToken.objects.all():
            r.created = after - timezone.timedelta(
                seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1
            )
            r.save()

        result = FileDownloadToken.get_paths(self.job, tokens)
        self.assertEqual(result, [None] * 5)

        # No records should exist in the database anymore
        self.assertFalse(FileDownloadToken.objects.all().exists())
