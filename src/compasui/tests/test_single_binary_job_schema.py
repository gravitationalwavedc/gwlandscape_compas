from os import path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from pathlib import Path
from django.conf import settings
from django.test import override_settings
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from compasui.utils.h5ToJson import read_h5_data_as_json


temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobSchema(CompasTestCase):
    def setUp(self):
        self.create_single_binary_job_mutation = """
            mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
                newSingleBinary(input: $input) {
                    result {
                        jobId
                        jsonData
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
                    'jsonData': '',
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
                    'jsonData': '',
                    'detailedOutputFilePath': ''
                }
            }
        }
        self.assertEqual(expected, response.data)

    @patch('compasui.views.run_compas')
    def test_celery_tasks_called(self, run_compas):
        run_compas.delay().get.return_value = TASK_SUCCESS

        self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        grid_file_path = path.join(settings.COMPAS_IO_PATH, '1', 'BSE_grid.txt')
        output_path = path.join(settings.COMPAS_IO_PATH, '1')
        detailed_output_file_path = path.join(settings.COMPAS_IO_PATH, '1', 'COMPAS_Output',
                                              'Detailed_Output', 'BSE_Detailed_Output_0.h5')

        run_compas.delay.assert_called_with(grid_file_path, output_path, detailed_output_file_path)

    @patch('compasui.views.run_compas')
    def test_new_single_binary_mutation_when_tasks_fail(self, run_compas):
        run_compas.delay().get.return_value = TASK_FAIL

        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        self.assertRaises(Exception, "1")
        self.assertEqual(self.expected_failed, response.data)

        run_compas.delay().get.return_value = TASK_TIMEOUT
        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )
        self.assertEqual(self.expected_failed, response.data)

    @patch('compasui.views.run_compas')
    def test_new_single_binary_mutation_when_tasks_succeed(self, run_compas):
        detailed_output_file_path = f'{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'

        run_compas.delay().get.return_value = TASK_SUCCESS

        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        expected_success = {
            'newSingleBinary': {
                'result': {
                    'jobId': '1',
                    'jsonData': read_h5_data_as_json("../compasui/tests/test_data/BSE_Detailed_Output_0.h5"),
                    'detailedOutputFilePath': detailed_output_file_path
                }
            }
        }
        run_compas.delay().get.assert_called_once()
        self.assertEqual(expected_success, response.data)
