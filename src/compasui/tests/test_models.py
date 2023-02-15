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

    def test_job_to_compas_options(self):
        """
        Check that a job object can be successfully converted to a json object
        with compas option as key and parameter value as value
        """

        job = CompasJob(user_id=1, name="second job", description="second job description")
        job.save()

        no_of_systems = BasicParameter(job=job, name="number_of_systems", value="100")
        no_of_systems.save()

        metallicity_distribution = BasicParameter(job=job, name="metallicity_distribution", value="ZSOLAR")
        metallicity_distribution.save()

        mass_transfer_accretion_efficiency_prescription = AdvancedParameter(job=job, name="mass_transfer_accretion_efficiency_prescription", value="FIXED")
        mass_transfer_accretion_efficiency_prescription.save()

        self.assertDictEqual(job.as_compas_options(), {
            "--number-of-systems": "100",
            "--metallicity-distribution": "ZSOLAR",
            "--mass-transfer-accretion-efficiency-prescription": "FIXED"
        })

    def test_job_to_compas_options_fail(self):
        """
        Check that job.as_compas_options() returns None if a parameter couldn't be mapped to a compas option
        """
        job = CompasJob(user_id=1, name="third job", description="third job description")
        job.save()

        no_of_systems = BasicParameter(job=job, name="no_of_systems", value="100")
        no_of_systems.save()

        mass_transfer_accretion_efficiency_prescription = AdvancedParameter(job=job,
                                                                            name="mass_transfer_accretion_efficiency_prescription",
                                                                            value="FIXED")
        mass_transfer_accretion_efficiency_prescription.save()

        self.assertIsNone(job.as_compas_options())