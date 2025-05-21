import os
from os import path
import shutil
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.conf import settings
from django.test import override_settings
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from compasui.utils.h5ToJson import read_h5_data_as_json
from compasui.tests.utils import silence_logging


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
            "input": {
                "mass1": 1.5,
                "mass2": 1.51,
                "metallicity": 0.02,
                "eccentricity": 0.1,
                "separation": 0.1,
                "commonEnvelopeAlpha": 0.1,
                "commonEnvelopeLambdaPrescription": "LAMBDA_FIXED",
                "fryerSupernovaEngine": "DELAYED",
            }
        }

        self.parameter_str = (
            "--initial-mass-1 1.5 --initial-mass-2 1.51 --metallicity 0.02 --eccentricity 0.1 "
            "--semi-major-axis 0.1 "
            "--common-envelope-alpha 0.1 --common-envelope-lambda-prescription LAMBDA_FIXED "
            "--fryer-supernova-engine DELAYED "
        )

        self.expected_failed = {
            "newSingleBinary": {
                "result": {"jobId": "", "jsonData": "", "detailedOutputFilePath": ""}
            }
        }
        self.test_detailed_output_file_path = (
            "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"
        )

    @silence_logging(logger_name="compasui.utils.h5ToJson")
    def test_h5_file_to_json(self):
        json_data = read_h5_data_as_json(self.test_detailed_output_file_path)
        self.assertIsNotNone(json_data)

        # Test it return None if the file doesn't exist
        json_data = read_h5_data_as_json(f"../{self.test_detailed_output_file_path}")
        self.assertIsNone(json_data)

    @silence_logging(logger_name="compasui.schema")
    @patch("compasui.views.run_compas")
    def test_celery_tasks_called(self, run_compas):
        run_compas.delay().get.return_value = TASK_SUCCESS

        self.client.execute(
            self.create_single_binary_job_mutation, self.single_binary_job_input
        )
        output_path = path.join(settings.COMPAS_IO_PATH, "1")

        run_compas.delay.assert_called_with(self.parameter_str, output_path)

    @silence_logging(logger_name="compasui.schema")
    @patch("compasui.views.run_compas")
    def test_new_single_binary_mutation_when_tasks_fail(self, run_compas):
        run_compas.delay().get.return_value = TASK_FAIL

        response = self.client.execute(
            self.create_single_binary_job_mutation, self.single_binary_job_input
        )

        self.assertRaises(Exception, "1")
        self.assertEqual(self.expected_failed, response.data)

        run_compas.delay().get.return_value = TASK_TIMEOUT
        response = self.client.execute(
            self.create_single_binary_job_mutation, self.single_binary_job_input
        )
        self.assertEqual(self.expected_failed, response.data)

    @patch("compasui.schema.get_plot_json", return_value="plot_json")
    @patch("compasui.views.run_compas")
    def test_new_single_binary_mutation_when_tasks_succeed(
        self, run_compas, get_plot_json
    ):
        detailed_output_file_url = f"{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5"
        # mock run_compas_output
        output_path = path.join(
            settings.COMPAS_IO_PATH, "1", "COMPAS_Output", "Detailed_Output"
        )
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_file_path = os.path.join(output_path, "BSE_Detailed_Output_0.h5")
        shutil.copy(self.test_detailed_output_file_path, output_file_path)
        run_compas.delay().get.return_value = TASK_SUCCESS

        response = self.client.execute(
            self.create_single_binary_job_mutation, self.single_binary_job_input
        )

        expected_success = {
            "newSingleBinary": {
                "result": {
                    "jobId": "1",
                    "jsonData": "plot_json",
                    "detailedOutputFilePath": detailed_output_file_url,
                }
            }
        }
        run_compas.delay().get.assert_called_once()
        self.assertEqual(expected_success, response.data)
        get_plot_json.assert_called_with(output_file_path)
