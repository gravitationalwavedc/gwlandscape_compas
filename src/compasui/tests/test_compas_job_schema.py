from datetime import datetime
import uuid

from django.contrib.auth import get_user_model
from graphql_relay import to_global_id
from compasui.models import CompasJob, FileDownloadToken
from compasui.tests.testcases import CompasTestCase
from unittest.mock import patch, Mock

User = get_user_model()


class TestCompasJobSchema(CompasTestCase):

    def setUp(self):
        self.user = User.objects.create(username="User1", first_name="first", last_name="last")

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
            'input': {
                'start': {
                    'name': 'first job',
                    'description': 'first job description',
                    'private': 'true'
                },
                'basicParameters': {
                    'numberOfSystems': '100'
                },
                'advancedParameters': {
                    'massTransferFa': '0.5',
                    'massTransferAccretionEfficiencyPrescription': 'FIXED',
                }
            }
        }

    @patch('compasui.views.requests')
    def test_create_compas_job_success(self, request_mock):

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"jobId":441}'
        mock_response.headers = "headers"

        request_mock.request.return_value = mock_response

        self.client.authenticate(self.user)

        response = self.client.execute(
            self.create_compas_job_mutation,
            self.compas_job_input
        )

        expected = {
            'newCompasJob': {
                'result': {
                    'jobId': to_global_id('CompasJobNode', CompasJob.objects.last().id)
                }
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)
        self.assertEqual(CompasJob.objects.all().count(), 1)

    @patch('compasui.views.requests')
    def test_create_compas_job_job_controller_fail(self, request_mock):

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = "Bad request"
        mock_response.headers = "headers"

        request_mock.request.side_effect = mock_response

        self.client.authenticate(self.user)

        response = self.client.execute(
            self.create_compas_job_mutation,
            self.compas_job_input
        )

        self.assertIsNotNone(response.errors)
        self.assertRaises(Exception, "Error submitting job, got error code: 400\n\nheaders\n\nBad request")

    @patch('compasui.models.request_file_list')
    @patch('compasui.schema.FileDownloadToken.create')
    def test_get_job_result_files(self, create_token, request_file_list):

        self.client.authenticate(self.user)

        job = CompasJob.objects.create(
            user_id=self.user.id,
            name="Test1",
            description="first job",
            job_controller_id=2,
            private=False
        )

        request_file_list.return_value = True, [{'path': '/job/file.txt', 'isDir': False, 'fileSize': 33, 'downloadToken': 1}]
        new_token = FileDownloadToken(
            job=job, token=uuid.uuid4(), path='/job/file.txt', created=datetime.now())
        create_token.return_value = [new_token]
        response = self.client.execute(
            f"""
            query{{
                compasResultFiles(jobId: "{to_global_id('CompasJobNode', job.id)}") {{
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
            'compasResultFiles': {
                'files': [
                    {'path': '/job/file.txt', 'isDir': False, 'fileSize': '33', 'downloadToken': str(new_token.token)}
                ]
            }
        }
        self.assertDictEqual(response.data, expected)
