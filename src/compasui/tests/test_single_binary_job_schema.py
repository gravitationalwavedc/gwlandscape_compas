from os import path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from pathlib import Path
from django.conf import settings
from django.test import override_settings
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT


temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobSchema(CompasTestCase):
    def setUp(self):
        self.create_single_binary_job_mutation = """
            mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
                newSingleBinary(input: $input) {
                    result {
                        jobId
                        gridFilePath
                        plotFilePath
                        vanPlotFilePath
                        detailedOutputFilePath
                    }
                }
            }
        """
        self.single_binary_job_input = {
            'input': {
                'mass1': 1.5,
                'mass2': 1.51,
                'metallicity': 0.02,
                'eccentricity': 0.1,
                'separation': 0.1,
                'commonEnvelopeAlpha': 0.1,
                'commonEnvelopeLambdaPrescription': 'LAMBDA_FIXED',
                'fryerSupernovaEngine': 'DELAYED',
                'kickVelocityDistribution': 'ZERO',
            }
        }

        self.expected_failed = {
            'newSingleBinary': {
                'result': {
                    'jobId': '',
                    'gridFilePath': '',
                    'plotFilePath': '',
                    'vanPlotFilePath': '',
                    'detailedOutputFilePath': ''
                }
            }
        }

    def test_new_single_binary_job_exception_no_redis_raised(self):
        # Not mocking tasks or redis. Tasks fail as celery cannot connect to redis
        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        expected = {
            'newSingleBinary': {
                'result': {
                    'jobId': '',
                    'gridFilePath': '',
                    'plotFilePath': '',
                    'vanPlotFilePath': '',
                    'detailedOutputFilePath': ''
                }
            }
        }
        self.assertEqual(expected, response.data)
