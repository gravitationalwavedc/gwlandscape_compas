from unittest.mock import patch
import os.path
from tempfile import TemporaryDirectory
from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase
from compasui.tasks import run_compas, run_detailed_evol_plotting
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT


class TestCeleryTasks(TestCase):

    def setUp(self):
        self.grid_file = './compasui/tests/test_data/BSE_grid.txt'
        self.output_dir = TemporaryDirectory()
        self.output_path = self.output_dir.name
        self.detailed_output_path = os.path.join(self.output_path, 'COMPAS_Output',
                                            'Detailed_Output', 'BSE_Detailed_Output_0.h5')
        self.plotting_file_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"

        self.detailed_plot_path = os.path.join(self.output_path, 'detailedEvolutionPlot.png')
        self.vanDenHeuval_plot_path = os.path.join(self.output_path, 'vanDenHeuvalPlot.png')
        self.evol_text_path = os.path.join(self.output_path, 'detailed_evol.txt')

    def tearDown(self):
        self.output_dir.cleanup()

    def test_run_compas_success(self):
        result = run_compas(self.grid_file, self.output_path, self.detailed_output_path)
        self.assertEqual(result, TASK_SUCCESS)

    @patch("compasui.tasks.run_compas_cmd")
    def test_run_compas_failure(self, run_compas_cmd):
        run_compas_cmd.side_effect = Exception('something went wrong')
        result = run_compas(self.grid_file, self.output_path, self.detailed_output_path)
        self.assertEqual(result, TASK_FAIL)

    @patch("compasui.tasks.run_compas_cmd")
    def test_run_compas_timeout(self, run_compas_cmd):
        run_compas_cmd.side_effect = SoftTimeLimitExceeded
        result = run_compas(self.grid_file, self.output_path, self.detailed_output_path)
        self.assertEqual(result, TASK_TIMEOUT)

    def test_run_detailed_evol_plotting_success(self):
        result = run_detailed_evol_plotting(TASK_SUCCESS, self.plotting_file_path, self.detailed_plot_path,
                                            self.vanDenHeuval_plot_path, self.evol_text_path)
        self.assertEqual(result, TASK_SUCCESS)

    @patch("compasui.tasks.plotting_main")
    def test_run_detailed_evol_plotting_failure(self, plotting_main):
        plotting_main.side_effect = Exception
        result = run_detailed_evol_plotting(TASK_SUCCESS, self.detailed_output_path, self.detailed_plot_path,
                                            self.vanDenHeuval_plot_path, self.evol_text_path)
        self.assertEqual(result, TASK_FAIL)

    @patch("compasui.tasks.plotting_main")
    def test_run_detailed_evol_plotting_timeout(self, plotting_main):
        plotting_main.side_effect = SoftTimeLimitExceeded
        result = run_detailed_evol_plotting(TASK_SUCCESS, self.detailed_output_path, self.detailed_plot_path,
                                            self.vanDenHeuval_plot_path, self.evol_text_path)
        self.assertEqual(result, TASK_TIMEOUT)

    def test_run_detailed_evol_plotting_failure_when_run_compas_fails(self):
        result = run_detailed_evol_plotting(TASK_FAIL, self.detailed_output_path, self.detailed_plot_path,
                                            self.vanDenHeuval_plot_path, self.evol_text_path)
        self.assertEqual(result, TASK_FAIL)

        result = run_detailed_evol_plotting(TASK_TIMEOUT, self.detailed_output_path, self.detailed_plot_path,
                                            self.vanDenHeuval_plot_path, self.evol_text_path)
        self.assertEqual(result, TASK_FAIL)
