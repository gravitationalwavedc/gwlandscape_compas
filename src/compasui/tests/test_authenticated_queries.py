from django.contrib.auth import get_user_model
from graphql_relay.node.node import to_global_id
from compasui.models import CompasJob
from compasui.tests.testcases import CompasTestCase
from unittest.mock import patch

User = get_user_model()


class TestQueriesWithAuthenticatedUser(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )
        self.client.authenticate(self.user)

    def perform_db_search_mock(*args, **kwargs):
        return True, [
            {
                "user": {"id": 1, "firstName": "buffy", "lastName": "summers"},
                "job": {"id": 1, "name": "Test1", "description": "A test job"},
                "history": [{"state": 500, "timestamp": "2020-01-01 12:00:00 UTC"}],
            },
            {
                "user": {"id": 1, "firstName": "buffy", "lastName": "summers"},
                "job": {"id": 2, "name": "Test2", "description": ""},
                "history": [{"state": 500, "timestamp": "2020-01-01 12:00:00 UTC"}],
            },
        ]

    def request_file_list_mock(*args, **kwargs):
        return True, [
            {"path": "/a/path/here", "isDir": False, "fileSize": 123, "downloadId": 1}
        ]

    def request_file_download_id_mock(*args, **kwargs):
        return True, 26

    def request_lookup_users_mock(*args, **kwargs):
        user = User.objects.first()
        if user:
            return True, [
                {
                    "userId": user.id,
                    "username": user.username,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                }
            ]
        return False, []

    @patch("compasui.schema.request_lookup_users")
    def test_compas_job_query(self, request_lookup_users):
        """
        compasJob node query should return a single job for an autheniticated user."
        """
        request_lookup_users.side_effect = self.request_lookup_users_mock
        job = CompasJob.objects.create(user_id=self.user.id)
        global_id = to_global_id("CompasJobNode", job.id)
        response = self.query(
            f"""
            query {{
                compasJob(id:"{global_id}"){{
                    id
                    name
                    userId
                    user
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
                "user": "buffy summers",
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

        # If it returns no user
        User.objects.first().delete()
        response = self.query(
            f"""
            query {{
                compasJob(id:"{global_id}"){{
                    user
                }}
            }}
            """
        )
        expected = {"compasJob": {"user": "Unknown User"}}
        self.assertDictEqual(
            expected, response.data, "compasJob query returned unexpected data."
        )
