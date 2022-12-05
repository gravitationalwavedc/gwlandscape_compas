from django.contrib.auth import get_user_model
from graphql_relay import to_global_id
from compasui.models import CompasJob
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
