from django.contrib.auth import get_user_model
from graphql_relay.node.node import to_global_id
from compasui.models import CompasJob
from compasui.tests.testcases import CompasTestCase

User = get_user_model()


class TestQueriesWithAuthenticatedUser(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")
        self.client.authenticate(self.user)

    def perform_db_search_mock(*args, **kwargs):
        return True, [
            {
                'user': {
                    'id': 1,
                    'firstName': 'buffy',
                    'lastName': 'summers'
                },
                'job': {
                    'id': 1,
                    'name': 'Test1',
                    'description': 'A test job'
                },
                'history': [{'state': 500, 'timestamp': '2020-01-01 12:00:00 UTC'}],
            },
            {
                'user': {
                    'id': 1,
                    'firstName': 'buffy',
                    'lastName': 'summers'
                },
                'job': {
                    'id': 2,
                    'name': 'Test2',
                    'description': ''
                },
                'history': [{'state': 500, 'timestamp': '2020-01-01 12:00:00 UTC'}],
            }
        ]

    def request_file_list_mock(*args, **kwargs):
        return True, [{'path': '/a/path/here', 'isDir': False, 'fileSize': 123, 'downloadId': 1}]

    def request_file_download_id_mock(*args, **kwargs):
        return True, 26

    def request_lookup_users_mock(*args, **kwargs):
        return '', [{
            'userId': 1,
            'username': 'buffy',
            'lastName': 'summers',
            'firstName': 'buffy'
        }]

    def test_compas_job_query(self):
        """
        compasJob node query should return a single job for an autheniticated user."
        """
        job = CompasJob.objects.create(user_id=self.user.id)
        global_id = to_global_id("CompasJobNode", job.id)
        response = self.client.execute(
            f"""
            query {{
                compasJob(id:"{global_id}"){{
                    id
                    name
                    userId
                    description
                    jobControllerId
                    private
                    lastUpdated
                    start {{
                        name
                        description
                        private
                    }}
                }}
            }}
            """
        )
        expected = {
            "compasJob": {
                "id": "Q29tcGFzSm9iTm9kZTox",
                "name": "",
                "userId": 1,
                "description": None,
                "jobControllerId": None,
                "private": False,
                "lastUpdated": job.last_updated.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "start": {"name": "", "description": None, "private": False},
            }
        }
        self.assertDictEqual(
            expected, response.data, "compasJob query returned unexpected data."
        )
