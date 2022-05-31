from unittest.mock import patch
import os.path
from tempfile import TemporaryDirectory
from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase
from compasui.tasks import run_compas
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT


class TestCeleryTasks(TestCase):
    def setUp(self):
        self.grid_file = './compasui/tests/test_data/BSE_grid.txt'

    def test_run_compas_success(self):
        print("Test run_compas task success")
        with TemporaryDirectory() as output_dir:
            output_path = output_dir
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                   'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(self.grid_file, output_path, detailed_output_path)
            self.assertEqual(result, TASK_SUCCESS)

    @patch("compasui.tasks.run_compas_cmd")
    def test_run_compas_failure(self, run_compas_cmd):
        print("Test run_compas task failure")
        run_compas_cmd.side_effect = Exception('something went wrong')
        result = None
        try:
            output_path = TemporaryDirectory().name
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(self.grid_file, output_path, detailed_output_path)
        except Exception:
            self.assertEqual(result, TASK_FAIL)

    @patch("compasui.tasks.run_compas_cmd")
    def test_run_compas_timeout(self, run_compas_cmd):
        print("Test run_compas task timeout")
        run_compas_cmd.side_effect = SoftTimeLimitExceeded
        result = None
        try:
            output_path = TemporaryDirectory().name
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(self.grid_file, output_path, detailed_output_path)
        except SoftTimeLimitExceeded:
            self.assertEqual(result, TASK_TIMEOUT)


