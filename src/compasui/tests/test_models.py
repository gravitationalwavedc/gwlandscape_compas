from django.test import TestCase

from gw_compas.jwt_tools import GWCloudUser
from compasui.models import CompasJob, Data, Label
from compasui.variables import compas_parameters
from compasui.views import update_compas_job


class TestCompasJobModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job = CompasJob.objects.create(
            user_id=1,
            name='Test Job',
            description='Test job description',
            private=False
        )
        cls.job.save()

    def test_update_privacy(self):
        """
        Check that update_compas_job view can update privacy of a job
        """
        self.assertEqual(self.job.private, False)

        user = GWCloudUser('bill')
        user.user_id = 1

        update_compas_job(self.job.id, user, True, [])

        self.job.refresh_from_db()
        self.assertEqual(self.job.private, True)

    def test_update_labels(self):
        """
        Check that update_compas_job view can update job labels
        """

        self.assertFalse(self.job.labels.exists())

        user = GWCloudUser('bill')
        user.user_id = 1

        update_compas_job(self.job.id, user, False, ['Bad Run', 'Review Requested'])

        self.job.refresh_from_db()
        self.assertQuerysetEqual(
            self.job.labels.all(),
            list(map(repr, Label.objects.filter(name__in=['Bad Run', 'Review Requested']))),
            ordered=False
        )


class TestModels(TestCase):
    def test_data_to_json(self):
        """
        Check that a Data object can be successfully converted to json
        """

        job = CompasJob(user_id=1)
        job.save()

        data = Data(job=job, data_choice=compas_parameters.FAKE_DATA[0])
        data.save()

        self.assertDictEqual(data.as_json(), {
            "id": data.id,
            "value": {
                "job": job.id,
                "choice": compas_parameters.FAKE_DATA[0],
                "source": "o1"
            }
        })
