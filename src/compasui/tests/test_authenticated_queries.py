from django.contrib.auth import get_user_model
from graphql_relay.node.node import to_global_id
from compasui.models import CompasJob
from compasui.tests.testcases import CompasTestCase
from unittest import mock

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

    def test_compas_jobs_query(self):
        """
        compasJobs query should return a list of personal jobs for an autheniticated user.
        """
        CompasJob.objects.create(
            user_id=self.user.id,
            name="Test1",
            job_controller_id=2,
            is_ligo_job=True
        )
        CompasJob.objects.create(
            user_id=self.user.id,
            name="Test2",
            job_controller_id=1,
            description="A test job",
            is_ligo_job=True
        )
        # This job shouldn't appear in the list because it belongs to another user.
        CompasJob.objects.create(user_id=4, name="Test3", job_controller_id=3)
        response = self.client.execute(
            """
            query {
                compasJobs{
                    edges {
                        node {
                            userId
                            name
                            description
                        }
                    }
                }
            }
            """
        )
        expected = {
            "compasJobs": {
                "edges": [
                    {"node": {"userId": 1, "name": "Test1", "description": None}},
                    {
                        "node": {
                            "userId": 1,
                            "name": "Test2",
                            "description": "A test job",
                        }
                    },
                ]
            }
        }
        self.assertDictEqual(
            response.data, expected, "compasJobs query returned unexpected data."
        )

    @mock.patch('compasui.schema.perform_db_search', side_effect=perform_db_search_mock)
    def test_public_compas_jobs_query(self, perform_db_search):
        CompasJob.objects.create(
            user_id=self.user.id, name="Test1", description="first job", job_controller_id=2, private=False
        )
        CompasJob.objects.create(
            user_id=self.user.id, name="Test2", job_controller_id=1, description="A test job", private=False
        )
        # This job shouldn't appear in the list because it's private.
        CompasJob.objects.create(user_id=4, name="Test3", job_controller_id=3, private=True)
        response = self.client.execute(
           """
           query {
               publicCompasJobs(search:"", timeRange:"all") {
                   edges {
                       node {
                           user
                           description
                           name
                           jobStatus {
                            name
                           }
                           timestamp
                           id
                       }
                    }
                }
            }
            """
        )
        expected = {'publicCompasJobs':
                    {'edges': [
                        {'node': {
                            'description': 'A test job',
                            'id': 'Q29tcGFzSm9iTm9kZTox',
                            'name': 'Test1',
                            'jobStatus': {
                                'name': 'Completed'
                            },
                            'timestamp': '2020-01-01 12:00:00 UTC',
                            'user': 'buffy summers'
                        }},
                        {'node': {
                            'description': '',
                            'id': 'Q29tcGFzSm9iTm9kZToy',
                            'name': 'Test2',
                            'jobStatus': {
                                'name': 'Completed',
                            },
                            'timestamp': '2020-01-01 12:00:00 UTC',
                            'user': 'buffy summers'
                        }}
                    ]}}
        self.assertDictEqual(response.data, expected, "publicCompasJobs query returned unexpected data.")

    @mock.patch('compasui.models.request_file_list', side_effect=request_file_list_mock)
    @mock.patch('compasui.models.request_file_download_id', side_effect=request_file_download_id_mock)
    def test_compas_result_files(self, request_file_list, request_file_download_id_mock):
        """
        CompasResultFiles query should return a file object.
        """
        job = CompasJob.objects.create(
            user_id=self.user.id,
            name="Test1",
            description="first job",
            job_controller_id=2,
            private=False
        )
        global_id = to_global_id("CompasJobNode", job.id)
        response = self.client.execute(
            f"""
            query {{
                compasResultFiles (jobId: "{global_id}") {{
                    files {{
                        path
                        isDir
                        fileSize
                        downloadId
                    }}
                }}
            }}
            """
        )
        expected = {
            'compasResultFiles': {
                'files': [
                    {'path': '/a/path/here', 'isDir': False, 'fileSize': 123, 'downloadId': '26'}
                ]
            }
        }
        self.assertDictEqual(response.data, expected)
