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
        with TemporaryDirectory() as output_path:
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(self.grid_file, output_path, detailed_output_path)
            self.assertEqual(result, TASK_FAIL)

    @patch("compasui.tasks.run_compas_cmd")
    def test_run_compas_timeout(self, run_compas_cmd):
        print("Test run_compas task timeout")
        run_compas_cmd.side_effect = SoftTimeLimitExceeded
        with TemporaryDirectory() as output_path:
            detailed_output_path = os.path.join(output_path, 'COMPAS_Output',
                                                'Detailed_Output', 'BSE_Detailed_Output_0.h5')
            result = run_compas(self.grid_file, output_path, detailed_output_path)
            self.assertEqual(result, TASK_TIMEOUT)

    def test_run_detailed_evol_plotting_success(self):
        print("Test run_detailed_evol_plotting success")
        with TemporaryDirectory() as output_dir:
            detailed_output_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"
            detailed_plot_path = os.path.join(output_dir, 'detailedEvolutionPlot.png')
            vanDenHeuval_plot_path = os.path.join(output_dir, 'vanDenHeuvalPlot.png')
            evol_text_path = os.path.join(output_dir, 'detailed_evol.txt')
            result = run_detailed_evol_plotting(TASK_SUCCESS, detailed_output_path,
                                                detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)
            self.assertEqual(result, TASK_SUCCESS)

    @patch("compasui.tasks.plotting_main")
    def test_run_detailed_evol_plotting_failure(self, plotting_main):
        print("Test run_detailed_evol_plotting failure")
        with TemporaryDirectory() as output_dir:
            detailed_output_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"
            detailed_plot_path = os.path.join(output_dir, 'detailedEvolutionPlot.png')
            vanDenHeuval_plot_path = os.path.join(output_dir, 'vanDenHeuvalPlot.png')
            evol_text_path = os.path.join(output_dir, 'detailed_evol.txt')
            plotting_main.side_effect = Exception
            result = run_detailed_evol_plotting(TASK_SUCCESS, detailed_output_path,
                                                detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)
            self.assertEqual(result, TASK_FAIL)

    @patch("compasui.tasks.plotting_main")
    def test_run_detailed_evol_plotting_timeout(self, plotting_main):
        print("Test run_detailed_evol_plotting timeout")
        with TemporaryDirectory() as output_dir:
            detailed_output_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"
            detailed_plot_path = os.path.join(output_dir, 'detailedEvolutionPlot.png')
            vanDenHeuval_plot_path = os.path.join(output_dir, 'vanDenHeuvalPlot.png')
            evol_text_path = os.path.join(output_dir, 'detailed_evol.txt')
            plotting_main.side_effect = SoftTimeLimitExceeded
            result = run_detailed_evol_plotting(TASK_SUCCESS, detailed_output_path,
                                                detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)
            self.assertEqual(result, TASK_TIMEOUT)

    def test_run_detailed_evol_plotting_failure_when_run_compas_fails(self):
        print("Test run_detailed_evol_plotting failure after run_compas task failure or timewout")
        with TemporaryDirectory() as output_dir:
            detailed_output_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"
            detailed_plot_path = os.path.join(output_dir, 'detailedEvolutionPlot.png')
            vanDenHeuval_plot_path = os.path.join(output_dir, 'vanDenHeuvalPlot.png')
            evol_text_path = os.path.join(output_dir, 'detailed_evol.txt')
            result = run_detailed_evol_plotting(TASK_FAIL, detailed_output_path,
                                                detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)
            self.assertEqual(result, TASK_FAIL)

            result = run_detailed_evol_plotting(TASK_TIMEOUT, detailed_output_path,
                                                detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)
            self.assertEqual(result, TASK_FAIL)
