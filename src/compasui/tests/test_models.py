from django.test import TestCase

from compasui.models import CompasJob, BasicParameter, AdvancedParameter


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

    # def test_update_privacy(self):
    #     """
    #     Check that update_compas_job view can update privacy of a job
    #     """
    #     self.assertEqual(self.job.private, False)
    #
    #     user = GWCloudUser('bill')
    #     user.user_id = 1
    #
    #     update_compas_job(self.job.id, user, True, [])
    #
    #     self.job.refresh_from_db()
    #     self.assertEqual(self.job.private, True)

    # def test_update_labels(self):
    #     """
    #     Check that update_compas_job view can update job labels
    #     """
    #
    #     self.assertFalse(self.job.labels.exists())
    #
    #     user = GWCloudUser('bill')
    #     user.user_id = 1
    #
    #     update_compas_job(self.job.id, user, False, ['Bad Run', 'Review Requested'])
    #
    #     self.job.refresh_from_db()
    #     self.assertQuerysetEqual(
    #         self.job.labels.all(),
    #         list(map(repr, Label.objects.filter(name__in=['Bad Run', 'Review Requested']))),
    #         ordered=False
    #     )


class TestModels(TestCase):
    def test_job_to_json(self):
        """
        Check that a job object can be successfully converted to json
        """

        job = CompasJob(user_id=1, name="first job", description="first job description")
        job.save()

        first = BasicParameter(job=job, name="first_parameter", value="1.0")
        first.save()

        second = BasicParameter(job=job, name="second_parameter", value="2.0")
        second.save()

        advanced = AdvancedParameter(job=job, name="advanced_parameter1", value="0.001")
        advanced.save()

        self.assertDictEqual(job.as_json(), {
            "name": "first job",
            "description": "first job description",
            "basic": {
                "first_parameter": "1.0",
                "second_parameter": "2.0"},
            "advanced": {
                "advanced_parameter1": "0.001"
            }
        })
