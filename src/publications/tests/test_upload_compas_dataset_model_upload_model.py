from django.conf import settings
from django.test import testcases
from django.utils import timezone

from publications.models import CompasDatasetModelUploadToken


class TestCompasDatasetModelUploadToken(testcases.TestCase):
    @classmethod
    def setUpTestData(cls):
        class TestUser:
            def __init__(self):
                self.user_id = 1234

        cls.user = TestUser()

    def test_create(self):
        # Test that a token can correctly be created for uploading a compas dataset model publication

        before = timezone.now()
        result = CompasDatasetModelUploadToken.create(self.user)
        after = timezone.now()

        self.assertEqual(result.user_id, self.user.user_id)
        self.assertTrue(result.token)
        self.assertTrue(before < result.created < after)

        self.assertEqual(CompasDatasetModelUploadToken.objects.count(), 1)

        result = CompasDatasetModelUploadToken.objects.last()
        self.assertEqual(result.user_id, self.user.user_id)
        self.assertTrue(result.token)
        self.assertTrue(before < result.created < after)

    def test_prune(self):
        # Test that CompasDatasetModelUploadToken objects older than settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY
        # are correctly removed from the database

        # Test that objects created now are not removed
        CompasDatasetModelUploadToken.create(self.user)
        after = timezone.now()

        CompasDatasetModelUploadToken.prune()

        self.assertEqual(CompasDatasetModelUploadToken.objects.all().count(), 1)

        # Check objects just inside the deletion time are not deleted
        r = CompasDatasetModelUploadToken.objects.last()
        r.created = after - timezone.timedelta(
            seconds=settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY - 1
        )
        r.save()

        CompasDatasetModelUploadToken.prune()

        self.assertEqual(CompasDatasetModelUploadToken.objects.all().count(), 1)

        # Check objects just outside the deletion time are deleted
        r.created = after - timezone.timedelta(
            seconds=settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY + 1
        )
        r.save()

        CompasDatasetModelUploadToken.prune()

        self.assertEqual(CompasDatasetModelUploadToken.objects.all().count(), 0)

    def test_get_by_token(self):
        before = timezone.now()
        ju_token = CompasDatasetModelUploadToken.create(self.user)
        after = timezone.now()

        token = ju_token.token

        result = CompasDatasetModelUploadToken.get_by_token(token)

        self.assertEqual(result.user_id, self.user.user_id)
        self.assertTrue(result.token)
        self.assertTrue(before < result.created < after)

        # Check that prune works as expected
        # Check objects just inside the deletion time are not deleted
        r = CompasDatasetModelUploadToken.objects.last()
        r.created = after - timezone.timedelta(
            seconds=settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY - 1
        )
        r.save()

        result = CompasDatasetModelUploadToken.get_by_token(token)

        self.assertEqual(result.user_id, self.user.user_id)
        self.assertTrue(result.token)

        # Set the object outside the expiry window
        r = CompasDatasetModelUploadToken.objects.last()
        r.created = after - timezone.timedelta(
            seconds=settings.COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY + 1
        )
        r.save()

        result = CompasDatasetModelUploadToken.get_by_token(token)

        self.assertEqual(result, None)

        # No records should exist in the database anymore
        self.assertFalse(CompasDatasetModelUploadToken.objects.all().exists())
