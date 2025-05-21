import uuid

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from graphql_relay import to_global_id
from compasui.models import CompasJob, FileDownloadToken
from compasui.tests.testcases import CompasTestCase
from compasui.tests.utils import silence_logging
from unittest.mock import patch, Mock

User = get_user_model()


class TestCompasJobSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="User1", first_name="first", last_name="last"
        )

        self.create_compas_job_mutation = """
            mutation NewCompasJobMutation($input: CompasJobMutationInput!) {
                newCompasJob(input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        self.compas_job_input = {
            "input": {
                "start": {
                    "name": "first_job",
                    "description": "first job description",
                    "private": True,
                },
                "basicParameters": {"numberOfSystems": "100"},
                "advancedParameters": {
                    "massTransferFa": "0.5",
                    "massTransferAccretionEfficiencyPrescription": "FIXED",
                },
            }
        }

    @patch("compasui.views.requests")
    def test_create_compas_job_success(self, request_mock):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"jobId":441}'
        mock_response.headers = "headers"

        request_mock.request.return_value = mock_response

        self.client.authenticate(self.user)

        response = self.client.execute(
            self.create_compas_job_mutation, self.compas_job_input
        )

        expected = {
            "newCompasJob": {
                "result": {
                    "jobId": to_global_id("CompasJobNode", CompasJob.objects.last().id)
                }
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)
        self.assertEqual(CompasJob.objects.all().count(), 1)

    @silence_logging(logger_name="compasui.views")
    @patch("compasui.views.requests")
    def test_create_compas_job_job_controller_fail(self, request_mock):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = "Bad request"
        mock_response.headers = "headers"

        request_mock.request.side_effect = mock_response

        self.client.authenticate(self.user)

        response = self.client.execute(
            self.create_compas_job_mutation, self.compas_job_input
        )

        self.assertIsNotNone(response.errors)
        self.assertRaises(
            Exception,
            "Error submitting job, got error code: 400\n\nheaders\n\nBad request",
        )

    @silence_logging(logger_name="compasui.schema")
    @patch("compasui.views.requests")
    def test_create_compas_job_name_exists(self, request_mock):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"jobId":441}'
        mock_response.headers = "headers"

        request_mock.request.return_value = mock_response

        self.client.authenticate(self.user)

        response = self.client.execute(
            self.create_compas_job_mutation, self.compas_job_input
        )

        response = self.client.execute(
            self.create_compas_job_mutation, self.compas_job_input
        )

        self.assertNotEqual(None, response.errors)
        self.assertRaises(Exception, "Job name is already in use!")

    @patch("compasui.models.request_file_list")
    @patch("compasui.schema.FileDownloadToken.create")
    def test_get_job_result_files(self, create_token, request_file_list):
        self.client.authenticate(self.user)

        job = CompasJob.objects.create(
            user_id=self.user.id,
            name="Test1",
            description="first job",
            job_controller_id=2,
            private=False,
        )

        request_file_list.return_value = (
            True,
            [
                {
                    "path": "/job/file.txt",
                    "isDir": False,
                    "fileSize": 33,
                    "downloadToken": 1,
                }
            ],
        )

        new_token = FileDownloadToken(
            job=job, token=uuid.uuid4(), path="/job/file.txt", created=timezone.now()
        )

        create_token.return_value = [new_token]

        response = self.client.execute(
            f"""
            query{{
                compasResultFiles(jobId: "{to_global_id("CompasJobNode", job.id)}") {{
                    files {{
                        path
                        isDir
                        fileSize
                        downloadToken
                    }}
                }}
            }}
            """
        )
        expected = {
            "compasResultFiles": {
                "files": [
                    {
                        "path": "/job/file.txt",
                        "isDir": False,
                        "fileSize": "33",
                        "downloadToken": str(new_token.token),
                    }
                ]
            }
        }
        self.assertDictEqual(response.data, expected)

    @patch("compasui.schema.request_file_download_id")
    def test_generate_file_download_id(self, request_file_download_id):
        self.client.authenticate(self.user)

        job = CompasJob.objects.create(
            user_id=self.user.id,
            name="Test1",
            description="first job",
            job_controller_id=2,
            private=False,
        )

        new_token = FileDownloadToken.objects.create(
            job=job,
            path="/job/file.txt",
        )

        # Test successful request when token is valid
        request_file_download_id.return_value = True, ["123456"]

        generate_file_download_id_mutation = """
            mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
                generateFileDownloadIds(input: $input) {
                    result
                }
            }
            """

        mutation_input = {
            "input": {
                "jobId": to_global_id("CompasJobNode", job.id),
                "downloadTokens": [str(new_token.token)],
            }
        }
        response = self.client.execute(
            generate_file_download_id_mutation, mutation_input
        )

        expected = {"generateFileDownloadIds": {"result": ["123456"]}}
        self.assertDictEqual(response.data, expected)

        # Test failure to get file download url
        request_file_download_id.return_value = (
            False,
            "Error getting job file download url",
        )

        response = self.client.execute(
            generate_file_download_id_mutation, mutation_input
        )
        expected = {"generateFileDownloadIds": None}
        self.assertDictEqual(response.data, expected)

        # Test failure when token is expired
        new_token.created = timezone.now() - timezone.timedelta(
            settings.FILE_DOWNLOAD_TOKEN_EXPIRY + 1
        )
        new_token.save()

        response = self.client.execute(
            generate_file_download_id_mutation, mutation_input
        )
        expected = {"generateFileDownloadIds": None}
        self.assertDictEqual(response.data, expected)

        request_file_download_id.return_value = (
            False,
            "Error getting job file download url",
        )
