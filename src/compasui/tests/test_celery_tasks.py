# from unittest.mock import patch
import os.path
from tempfile import TemporaryDirectory
from compasui.tasks import run_compas
# from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase
from compasui.utils.constants import TASK_SUCCESS


class TestCeleryTasks(TestCase):

    def test_run_compas_success(self):
        print("Test run_compas task success")
        grid_file = './compasui/tests/test_data/BSE_grid.txt'
        with TemporaryDirectory() as output_dir:
            output_path = output_dir
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                   'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(grid_file, output_path, detailed_output_path)
            self.assertEqual(result, TASK_SUCCESS)

