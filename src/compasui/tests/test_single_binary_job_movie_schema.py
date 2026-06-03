from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.conf import settings
from django.test import override_settings
from compasui.tests.testcases import CompasTestCase
from compasui.tests.utils import silence_logging


temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobMovieSchema(CompasTestCase):
    def setUp(self):
        self.create_single_binary_job_movie_mutation = """
            mutation NewSingleBinaryJobMovieMutation($input: SingleBinaryJobMovieMutationInput!) {
                newSingleBinaryMovie(input: $input) {
                    result {
                        movieFilePath
                    }
                }
            }
        """
        self.single_binary_job_movie_input = {
            "input": {
                "jobId": "1",
                "scaling": "log",
                "images": "default",
            }
        }

        self.expected_failed = {
            "newSingleBinaryMovie": {"result": {"movieFilePath": ""}}
        }

    @patch("compasui.schema.create_single_binary_job_movie")
    def test_celery_tasks_called_for_movie(self, create_single_binary_job_movie):
        self.query(
            self.create_single_binary_job_movie_mutation,
            input_data=self.single_binary_job_movie_input["input"],
        )

        create_single_binary_job_movie.assert_called_with(
            job_id="1",
            scaling="log",
            images="default",
        )

    @silence_logging(logger_name="compasui.schema")
    @patch(
        "compasui.schema.create_single_binary_job_movie",
        side_effect=Exception("VIMES failed"),
    )
    def test_new_single_binary_movie_mutation_when_task_fails(
        self, create_single_binary_job_movie
    ):
        response = self.query(
            self.create_single_binary_job_movie_mutation,
            input_data=self.single_binary_job_movie_input["input"],
        )

        self.assertEqual(self.expected_failed, response.data)

    @patch("compasui.schema.create_single_binary_job_movie")
    def test_new_single_binary_movie_mutation_when_task_succeeds(
        self, create_single_binary_job_movie
    ):
        response = self.query(
            self.create_single_binary_job_movie_mutation,
            input_data=self.single_binary_job_movie_input["input"],
        )

        expected_success = {
            "newSingleBinaryMovie": {
                "result": {
                    "movieFilePath": f"{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/log_default_movie.mp4",
                }
            }
        }
        self.assertEqual(expected_success, response.data)
