from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from graphql_relay.node.node import to_global_id

from compasui.models import SingleBinaryJob
from compasui.tests.testcases import CompasTestCase
from compasui.tests.utils import silence_logging

temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobMovieSchema(CompasTestCase):
    def setUp(self):
        self.test_task_id = "test-task-id"
        self.single_binary_job_movie_results_query = """
            query ($id: ID!, $scaling: String, $images: String){
                singleBinaryJob(id: $id) {
                    movieFileUrl(scaling: $scaling, images: $images)
                }
            }
        """
        self.single_binary_job_node_movie_input = {
            "input": {
                "id": to_global_id("SingleBinaryJobNode", 1),
                "scaling": "log",
                "images": "default",
            }
        }
        self.create_single_binary_job_movie_mutation = """
            mutation NewSingleBinaryJobMovieMutation($input: SingleBinaryJobMovieMutationInput!) {
                newSingleBinaryMovie(input: $input) {
                    result {
                        taskId
                    }
                }
            }
        """
        self.single_binary_job_movie_input = {
            "input": {
                "jobId": to_global_id("SingleBinaryJobNode", 1),
                "scaling": "log",
                "images": "default",
            }
        }

        self.expected_failed = {
            "newSingleBinaryMovie": {"result": {"movieFilePath": ""}}
        }
        self.test_output_file_path = (
            Path(settings.COMPAS_IO_PATH) / "1" / "COMPAS_Output" / "Detailed_Output"
        )
        self.test_output_file_path.mkdir(parents=True, exist_ok=True)
        self.test_output_file = self.test_output_file_path / "BSE_Detailed_Output_0.h5"
        self.test_output_file.touch(exist_ok=True)

    @patch("compasui.views.run_vimes")
    def test_celery_tasks_called_for_movie(self, run_vimes):
        run_vimes.delay().id = self.test_task_id

        response = self.query(
            self.create_single_binary_job_movie_mutation,
            input_data=self.single_binary_job_movie_input["input"],
        )

        run_vimes.delay.assert_called_with(
            str(self.test_output_file_path), "log", "default"
        )
        self.assertEqual(
            {
                "newSingleBinaryMovie": {
                    "result": {
                        "taskId": self.test_task_id,
                    }
                }
            },
            response.data,
        )

    @silence_logging(logger_name="compasui.schema")
    def test_new_single_binary_job_movie_results_query(self):
        test_job = SingleBinaryJob.objects.create(
            mass1=1.0, mass2=0.5, metallicity=0.0, eccentricity=0.0
        )

        # Movie file doesn't exist, return None
        response = self.query(
            self.single_binary_job_movie_results_query,
            variables={
                "id": to_global_id("SingleBinaryJobNode", test_job.id),
                "scaling": "log",
                "images": "default",
            },
        )

        self.assertIsNone(response.data["singleBinaryJob"]["movieFileUrl"])

        # Movie file exists, return URL
        movie_file = self.test_output_file_path / "log_default_movie.mp4"
        movie_file.touch(exist_ok=True)

        response = self.query(
            self.single_binary_job_movie_results_query,
            variables={
                "id": to_global_id("SingleBinaryJobNode", test_job.id),
                "scaling": "log",
                "images": "default",
            },
        )

        self.assertEqual(
            str(
                Path(settings.MEDIA_URL)
                / "jobs"
                / str(test_job.id)
                / "COMPAS_Output"
                / "Detailed_Output"
                / "log_default_movie.mp4"
            ),
            response.data["singleBinaryJob"]["movieFileUrl"],
        )
