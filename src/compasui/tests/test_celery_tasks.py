import os
from unittest.mock import patch
from tempfile import TemporaryDirectory
from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase
from compasui.tasks import run_compas
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from compasui.tests.utils import silence_logging


class TestCeleryTasks(TestCase):
    def setUp(self):
        self.parameter_str = (
            "--initial-mass-1 35.0 --initial-mass-2 31.0 --metallicity 0.001 "
            "--eccentricity 0.0 --semi-major-axis 1.02 --kick-magnitude-1 0.0 "
            "--kick-magnitude-2 0.0 --common-envelope-alpha 1.0 "
            "--common-envelope-lambda-prescription LAMBDA_NANJING "
            "--remnant-mass-prescription FRYER2012 --fryer-supernova-engine DELAYED "
            "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC "
            "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 "
        )
        self.output_dir = TemporaryDirectory()
        self.output_path = self.output_dir.name
        # Ensure the COMPAS_ROOT_DIR environment variable is set for testing
        os.environ["COMPAS_ROOT_DIR"] = "/mock/path"

        # Prepare expected values for assertions
        compas_executable = f"/mock/path/src/COMPAS"
        self.expected_command = (
            f"{compas_executable} --detailed-output --number-of-systems 1 "
            f"--output-path {self.output_path} {self.parameter_str}"
        )
        self.expected_output_file = (
            f"{self.output_path}/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5"
        )

    def tearDown(self):
        self.output_dir.cleanup()

    @patch("compasui.tasks.call")
    @patch("compasui.tasks.check_output_file_generated")
    def test_run_compas_success(self, mock_check_output, mock_subprocess_call):
        # Set up the mocks
        mock_check_output.return_value = TASK_SUCCESS
        mock_subprocess_call.return_value = 0  # Successful call returns 0

        # Run the test
        result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        self.assertEqual(result, TASK_SUCCESS)
        mock_subprocess_call.assert_called_once_with(self.expected_command, shell=True)
        mock_check_output.assert_called_once_with(self.expected_output_file)

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.call")
    def test_run_compas_failure(self, mock_subprocess_call):
        # Set up the mocks
        mock_subprocess_call.side_effect = Exception("something went wrong")
        # We don't expect check_output_file_generated to be called due to the exception

        # Run the test
        result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        self.assertEqual(result, TASK_FAIL)
        mock_subprocess_call.assert_called_once_with(self.expected_command, shell=True)

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.call")
    def test_run_compas_timeout(self, mock_subprocess_call):
        # Set up the mocks
        mock_subprocess_call.side_effect = SoftTimeLimitExceeded()
        # We don't expect check_output_file_generated to be called due to the exception

        # Run the test
        result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        self.assertEqual(result, TASK_TIMEOUT)
        mock_subprocess_call.assert_called_once_with(self.expected_command, shell=True)

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.call")
    @patch("compasui.tasks.check_output_file_generated")
    def test_run_compas_file_check_timeout(
        self, mock_check_output, mock_subprocess_call
    ):
        # Set up the mocks
        mock_check_output.side_effect = (
            SoftTimeLimitExceeded()
        )  # Simulate Celery timeout
        mock_subprocess_call.return_value = 0  # Command runs successfully

        # Run the test
        result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        self.assertEqual(result, TASK_TIMEOUT)
        mock_subprocess_call.assert_called_once_with(self.expected_command, shell=True)
        mock_check_output.assert_called_once_with(self.expected_output_file)


class TestCheckOutputFileGenerated(TestCase):
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_file_exists_immediately(self, mock_sleep, mock_exists):
        # Set up the mocks
        mock_exists.return_value = True

        # Run the test
        from compasui.tasks import check_output_file_generated

        result = check_output_file_generated("some/file/path.txt")

        # Assertions
        self.assertEqual(result, TASK_SUCCESS)
        mock_exists.assert_called_once_with("some/file/path.txt")
        mock_sleep.assert_not_called()

    @patch("os.path.exists")
    @patch("time.sleep")
    def test_file_exists_after_delay(self, mock_sleep, mock_exists):
        # Set up the mocks
        mock_exists.side_effect = [False, False, True]

        # Run the test
        from compasui.tasks import check_output_file_generated

        result = check_output_file_generated("some/file/path.txt")

        # Assertions
        self.assertEqual(result, TASK_SUCCESS)
        self.assertEqual(mock_exists.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("os.path.exists")
    @patch("time.sleep")
    def test_celery_timeout(self, mock_sleep, mock_exists):
        # Set up the mocks
        mock_exists.return_value = False
        mock_sleep.side_effect = SoftTimeLimitExceeded()  # Simulate Celery timeout

        # Run the test
        from compasui.tasks import check_output_file_generated

        with self.assertRaises(SoftTimeLimitExceeded):
            check_output_file_generated("some/file/path.txt")

        # Assertions
        self.assertGreaterEqual(mock_exists.call_count, 1)
