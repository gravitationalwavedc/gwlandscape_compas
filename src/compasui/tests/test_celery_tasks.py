import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, call, patch

from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase

from compasui.tasks import run_compas, run_vimes
from compasui.tests.utils import silence_logging
from compasui.utils.constants import (
    COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_NANJING_VALUE,
    FRYER_SUPERNOVA_ENGINE_DELAYED_VALUE,
    MASS_TRANSFER_ACCRETION_EFFICIENCY_PRESCRIPTION_THERMAL_VALUE,
    MASS_TRANSFER_ANGULAR_MOMENTUM_LOSS_PRESCRIPTION_ISOTROPIC_VALUE,
    REMNANT_MASS_PRESCRIPTION_FRYER2012_VALUE,
)


class TestSingleBinaryCeleryTasks(TestCase):
    def setUp(self):
        self.parameters = {
            "--initial-mass-1": 35.0,
            "--initial-mass-2": 31.0,
            "--metallicity": 0.001,
            "--eccentricity": 0.0,
            "--semi-major-axis": 1.02,
            "--kick-magnitude-1": 0.0,
            "--kick-magnitude-2": 0.0,
            "--common-envelope-alpha": 1.0,
            "--common-envelope-lambda-prescription": COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_NANJING_VALUE,
            "--remnant-mass-prescription": REMNANT_MASS_PRESCRIPTION_FRYER2012_VALUE,
            "--fryer-supernova-engine": FRYER_SUPERNOVA_ENGINE_DELAYED_VALUE,
            "--mass-transfer-angular-momentum-loss-prescription": MASS_TRANSFER_ANGULAR_MOMENTUM_LOSS_PRESCRIPTION_ISOTROPIC_VALUE,
            "--mass-transfer-accretion-efficiency-prescription": MASS_TRANSFER_ACCRETION_EFFICIENCY_PRESCRIPTION_THERMAL_VALUE,
            "--mass-transfer-fa": 0.5,
        }
        self.output_dir = TemporaryDirectory()
        self.output_path = Path(self.output_dir.name)
        self.detailed_output_path = (
            self.output_path / "COMPAS_Output" / "Detailed_Output"
        )
        self.detailed_output_path.mkdir(exist_ok=True, parents=True)

        # Ensure the COMPAS_ROOT_DIR environment variable is set for testing
        os.environ["COMPAS_ROOT_DIR"] = "/mock/path"

        # Prepare expected values for assertions
        compas_executable = "/mock/path/src/COMPAS"
        self.expected_command = [
            compas_executable,
            "--detailed-output",
            "--number-of-systems",
            "1",
            "--output-path",
            str(self.output_path),
            "--initial-mass-1",
            "35.0",
            "--initial-mass-2",
            "31.0",
            "--metallicity",
            "0.001",
            "--eccentricity",
            "0.0",
            "--semi-major-axis",
            "1.02",
            "--kick-magnitude-1",
            "0.0",
            "--kick-magnitude-2",
            "0.0",
            "--common-envelope-alpha",
            "1.0",
            "--common-envelope-lambda-prescription",
            "LAMBDA_NANJING",
            "--remnant-mass-prescription",
            "FRYER2012",
            "--fryer-supernova-engine",
            "DELAYED",
            "--mass-transfer-angular-momentum-loss-prescription",
            "ISOTROPIC",
            "--mass-transfer-accretion-efficiency-prescription",
            "THERMAL",
            "--mass-transfer-fa",
            "0.5",
        ]
        self.expected_output_file = (
            self.detailed_output_path / "BSE_Detailed_Output_0.h5"
        )
        self.expected_json_file = self.detailed_output_path / "plot_data.json"
        self.test_json_str = json.dumps({"key": "value"})

    def tearDown(self):
        self.output_dir.cleanup()

    @patch("compasui.tasks.get_plot_json")
    @patch("compasui.tasks.run")
    def test_run_compas_success(self, mock_subprocess_run, mock_get_plot_json):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=0
        )  # Successful run returns 0
        mock_subprocess_run.side_effect = self.expected_output_file.touch()
        mock_get_plot_json.return_value = self.test_json_str

        # Run the test
        result = run_compas(self.parameters, str(self.output_path))

        # Assertions
        self.assertEqual(result[0], str(self.expected_output_file))
        self.assertEqual(result[1], str(self.expected_json_file))
        self.assertEqual(
            self.test_json_str,
            Path(result[1]).read_text(encoding="utf-8"),
        )
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )
        self.assertTrue(self.expected_json_file.exists())

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_compas_failure(self, mock_subprocess_run):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=1
        )  # Successful run returns 0

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_compas(self.parameters, str(self.output_path))

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

        # Run the test
        with self.assertRaises(SoftTimeLimitExceeded):
            run_compas(self.parameters, str(self.output_path))

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_compas_success_no_output_file(self, mock_subprocess_run):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=0
        )  # Successful run returns 0

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_compas(self.parameters, str(self.output_path))

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_command, capture_output=True, text=True, check=False
        )

        self.assertIn(
            f"Expected output file not found: {self.expected_output_file}",
            str(exc.exception),
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.get_plot_json")
    @patch("compasui.tasks.run")
    @patch("compasui.tasks.Path.write_text")
    def test_run_compas_success_no_json_file(
        self, _, mock_subprocess_run, mock_get_plot_json
    ):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=0
        )  # Successful run returns 0
        mock_subprocess_run.side_effect = self.expected_output_file.touch()
        mock_get_plot_json.return_value = self.test_json_str

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_compas(self.parameters, str(self.output_path))

        self.assertIn(
            f"Expected json file not found: {self.expected_json_file}",
            str(exc.exception),
        )


class TestSingleBinaryMovieCeleryTasks(TestCase):
    def setUp(self):
        self.output_dir = TemporaryDirectory()
        self.output_path = Path(self.output_dir.name)
        self.detailed_output_path = (
            self.output_path / "COMPAS_Output" / "Detailed_Output"
        )
        self.detailed_output_path.mkdir(exist_ok=True, parents=True)

        self.expected_frames_file = self.detailed_output_path / "frames_data.npz"
        self.expected_output_file = self.detailed_output_path / "log_default_movie.mp4"

        # Prepare expected values for assertions
        self.expected_vimes_preprocess_command = [
            "vimes-preprocess",
            str(self.detailed_output_path / "BSE_Detailed_Output_0.h5"),
            str(self.expected_frames_file),
        ]
        self.expected_vimes_command = [
            "vimes",
            str(self.expected_frames_file),
            "--scaling",
            "log",
            "--images",
            "default",
            "--save-mp4",
            str(self.expected_output_file),
            "--no-display",
        ]

    def tearDown(self):
        self.output_dir.cleanup()

    @patch("compasui.tasks.run")
    def test_run_vimes_success(self, mock_subprocess_run):
        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "vimes-preprocess":
                self.expected_frames_file.touch()
            elif cmd[0] == "vimes":
                self.expected_output_file.touch()
            return Mock(returncode=0)

        # Set up the mocks
        mock_subprocess_run.side_effect = mock_run

        # Run the test
        result = run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        self.assertEqual(result, str(self.expected_output_file))
        mock_subprocess_run.assert_has_calls(
            [
                call(
                    self.expected_vimes_preprocess_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
                call(
                    self.expected_vimes_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
            ]
        )

    def test_run_vimes_movie_file_exists_success(self):
        self.expected_output_file.touch()  # Create the movie file to simulate it already exists

        # Run the test
        result = run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        self.assertEqual(result, str(self.expected_output_file))

    @patch("compasui.tasks.run")
    def test_run_vimes_frames_file_exists_success(self, mock_subprocess_run):
        self.expected_frames_file.touch()

        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "vimes":
                self.expected_output_file.touch()
            return Mock(returncode=0)

        # Set up the mocks
        mock_subprocess_run.side_effect = mock_run

        # Run the test
        result = run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        self.assertEqual(result, str(self.expected_output_file))
        mock_subprocess_run.assert_called_once_with(
            self.expected_vimes_command, capture_output=True, text=True, check=False
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_vimes_preprocess_failure(self, mock_subprocess_run):
        # Set up the mocks
        mock_subprocess_run.return_value = Mock(
            returncode=1
        )  # Simulate vimes-preprocess failure

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_vimes_preprocess_command,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn("vimes-preprocess exited with code 1", str(exc.exception))

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_vimes_failure(self, mock_subprocess_run):
        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "vimes-preprocess":
                self.expected_frames_file.touch()
                return Mock(returncode=0)
            elif cmd[0] == "vimes":
                self.expected_output_file.touch()
                return Mock(returncode=1)  # Simulate vimes failure

        # Set up the mocks
        mock_subprocess_run.side_effect = mock_run

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        mock_subprocess_run.assert_has_calls(
            [
                call(
                    self.expected_vimes_preprocess_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
                call(
                    self.expected_vimes_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
            ]
        )

        self.assertIn("vimes exited with code 1", str(exc.exception))

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_vimes_preprocess_frames_creation_failure(self, mock_subprocess_run):
        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "vimes-preprocess":
                return Mock(returncode=0)

        # Set up the mocks
        mock_subprocess_run.side_effect = mock_run

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        mock_subprocess_run.assert_called_once_with(
            self.expected_vimes_preprocess_command,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn(
            f"Expected vimes-preprocess frames file not found: {self.expected_frames_file}",
            str(exc.exception),
        )

    @silence_logging(logger_name="compasui.tasks")
    @patch("compasui.tasks.run")
    def test_run_vimes_movie_creation_failure(self, mock_subprocess_run):
        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "vimes-preprocess":
                self.expected_frames_file.touch()
                return Mock(returncode=0)
            elif cmd[0] == "vimes":
                return Mock(returncode=0)

        # Set up the mocks
        mock_subprocess_run.side_effect = mock_run

        # Run the test
        with self.assertRaises(Exception) as exc:
            run_vimes(self.detailed_output_path, scaling="log", images="default")

        # Assertions
        mock_subprocess_run.assert_has_calls(
            [
                call(
                    self.expected_vimes_preprocess_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
                call(
                    self.expected_vimes_command,
                    capture_output=True,
                    text=True,
                    check=False,
                ),
            ]
        )

        self.assertIn(
            f"Expected movie file not found: {self.expected_output_file}",
            str(exc.exception),
        )
