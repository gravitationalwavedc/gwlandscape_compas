from pathlib import Path
import json
import shutil
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.conf import settings
from django.test import override_settings
from graphql_relay.node.node import to_global_id
from compasui.models import SingleBinaryJob
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import (
    COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_FIXED_VALUE,
    FRYER_SUPERNOVA_ENGINE_DELAYED_VALUE,
)
from compasui.utils.h5ToJson import read_h5_data_as_json
from compasui.tests.utils import silence_logging


temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobSchema(CompasTestCase):
    def setUp(self):
        self.single_binary_job_results_query = """
            query ($id: ID!){
                singleBinaryJob(id: $id) {
                    detailedOutputFilePath
                    plotJsonData
                }
            }
        """
        self.test_task_id = "test-task-id"
        self.create_single_binary_job_mutation = """
            mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
                newSingleBinary(input: $input) {
                    result {
                        taskId
                        jobId
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
        self.parameters = {
            "--initial-mass-1": 1.5,
            "--initial-mass-2": 1.51,
            "--metallicity": 0.02,
            "--eccentricity": 0.1,
            "--semi-major-axis": 0.1,
            "--common-envelope-alpha": 0.1,
            "--common-envelope-lambda-prescription": COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_FIXED_VALUE,
            "--fryer-supernova-engine": FRYER_SUPERNOVA_ENGINE_DELAYED_VALUE,
        }

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
    def test_new_single_binary_job_mutation_returns(self, run_compas):
        run_compas.delay().id = self.test_task_id

        response = self.query(
            self.create_single_binary_job_mutation,
            input_data=self.single_binary_job_input["input"],
        )
        output_path = Path(settings.COMPAS_IO_PATH) / "1"
        run_compas.delay.assert_called_with(self.parameters, str(output_path))
        self.assertEqual(
            {
                "newSingleBinary": {
                    "result": {
                        "taskId": self.test_task_id,
                        "jobId": to_global_id(
                            "SingleBinaryJobNode", SingleBinaryJob.objects.last().id
                        ),
                    }
                }
            },
            response.data,
        )

    @silence_logging(logger_name="compasui.schema")
    def test_new_single_binary_job_results_query(self):
        test_job = SingleBinaryJob.objects.create(
            mass1=1.0, mass2=0.5, metallicity=0.0, eccentricity=0.0
        )

        detailed_output_file_url = (
            Path(settings.MEDIA_URL)
            / "jobs"
            / str(test_job.id)
            / "COMPAS_Output"
            / "Detailed_Output"
            / "BSE_Detailed_Output_0.h5"
        )

        # mock run_compas_output
        output_path = (
            Path(settings.COMPAS_IO_PATH)
            / str(test_job.id)
            / "COMPAS_Output"
            / "Detailed_Output"
        )
        output_path.mkdir(parents=True, exist_ok=True)

        output_file_path = output_path / "BSE_Detailed_Output_0.h5"
        plot_json_file_path = output_path / "plot_data.json"
        shutil.copy(self.test_detailed_output_file_path, output_file_path)
        test_json_string = "json_string"
        plot_json_file_path.write_text(json.dumps(test_json_string), encoding="utf-8")

        response = self.query(
            self.single_binary_job_results_query,
            variables={"id": to_global_id("SingleBinaryJobNode", test_job.id)},
        )

        self.assertEqual(
            str(detailed_output_file_url),
            response.data["singleBinaryJob"]["detailedOutputFilePath"],
        )
        self.assertEqual(
            test_json_string,
            json.loads(response.data["singleBinaryJob"]["plotJsonData"]),
        )
