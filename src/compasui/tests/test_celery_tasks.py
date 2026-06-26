import os
from pathlib import Path
from unittest.mock import patch, Mock
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

    @patch("compasui.tasks.run")
    @patch("compasui.tasks.Path.exists")
    def test_run_compas_success(self, mock_path_exists, mock_subprocess_run):
        # Set up the mocks
        mock_path_exists.return_value = True
        mock_subprocess_run.return_value = Mock(
            returncode=0
        )  # Successful run returns 0

        # Run the test
        result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        self.assertEqual(result, self.expected_output_file)
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_compas_failure(self, mock_subprocess_run):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=1
        )  # Successful run returns 0
        # We don't expect check_output_file_generated to be called due to the exception

        # Run the test
        with self.assertRaises(Exception) as exc:
            result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

        self.assertIn("COMPAS exited with code 1", str(exc.exception))

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_compas_timeout(self, mock_subprocess_run):
        # Set up the mocks
        mock_subprocess_run.side_effect = SoftTimeLimitExceeded()
        # We don't expect check_output_file_generated to be called due to the exception

        # Run the test
        with self.assertRaises(SoftTimeLimitExceeded):
            result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    @patch("compasui.tasks.Path.exists")
    def test_run_compas_success_no_file(self, mock_path_exists, mock_subprocess_run):
        # Set up the mocks
        mock_path_exists.return_value = False
        mock_subprocess_run.return_value = Mock(
            returncode=0
        )  # Successful run returns 0

        # Run the test
        with self.assertRaises(Exception) as exc:
            result = run_compas(self.parameter_str, self.output_path)

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

        self.assertIn(
            f"Expected output file not found: {self.expected_output_file}",
            str(exc.exception),
        )
