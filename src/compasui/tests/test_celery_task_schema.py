from tempfile import TemporaryDirectory
from unittest.mock import patch, Mock
from celery import states
from celery.exceptions import SoftTimeLimitExceeded
from django.test import override_settings
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT, TASK_PENDING


temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobSchema(CompasTestCase):
    def setUp(self):
        self.celery_task_status_query = """
            query ($taskId: String!){
                celeryTaskStatus(taskId: $taskId) {
                    status
                    error
                }
            }
        """
        self.celery_task_status_input = {"taskId": "test-task-id"}

    @patch("compasui.schema.AsyncResult")
    def test_celery_task_timeout(self, mock_async_result):
        mock_async_result.return_value = Mock(
            state=states.FAILURE, result=SoftTimeLimitExceeded()
        )
        response = self.query(
            self.celery_task_status_query, variables=self.celery_task_status_input
        )
        self.assertEqual(TASK_TIMEOUT, response.data["celeryTaskStatus"]["status"])
        self.assertEqual(
            "Soft time limit exceeded", response.data["celeryTaskStatus"]["error"]
        )

    @patch("compasui.schema.AsyncResult")
    def test_celery_task_failure(self, mock_async_result):
        mock_async_result.return_value = Mock(
            state=states.FAILURE, result=Exception("Task failed with code 1")
        )
        response = self.query(
            self.celery_task_status_query, variables=self.celery_task_status_input
        )
        self.assertEqual(TASK_FAIL, response.data["celeryTaskStatus"]["status"])
        self.assertEqual(
            "Task failed with code 1", response.data["celeryTaskStatus"]["error"]
        )

    @patch("compasui.schema.AsyncResult")
    def test_celery_task_pending(self, mock_async_result):
        mock_async_result.return_value = Mock(state=states.PENDING)
        response = self.query(
            self.celery_task_status_query, variables=self.celery_task_status_input
        )
        self.assertEqual(TASK_PENDING, response.data["celeryTaskStatus"]["status"])
        self.assertIsNone(response.data["celeryTaskStatus"]["error"])

    @patch("compasui.schema.AsyncResult")
    def test_celery_task_success(self, mock_async_result):
        mock_async_result.return_value = Mock(
            state=states.SUCCESS, result="test/output/file_path"
        )
        response = self.query(
            self.celery_task_status_query, variables=self.celery_task_status_input
        )
        self.assertEqual(TASK_SUCCESS, response.data["celeryTaskStatus"]["status"])
        self.assertIsNone(response.data["celeryTaskStatus"]["error"])
