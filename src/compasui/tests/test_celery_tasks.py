from unittest.mock import patch
import os.path
from tempfile import TemporaryDirectory
from celery.exceptions import SoftTimeLimitExceeded
from django.test import TestCase
from compasui.tasks import run_compas
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT


class TestCeleryTasks(TestCase):

    def setUp(self):
        # self.grid_file = './compasui/tests/test_data/BSE_grid.txt'
        self.parameter_str = ('--initial-mass-1 35.0 --initial-mass-2 31.0 --metallicity 0.001 '
                               '--eccentricity 0.0 --semi-major-axis 1.02 --kick-magnitude-1 0.0 '
                               '--kick-magnitude-2 0.0 --common-envelope-alpha 1.0 '
                               '--common-envelope-lambda-prescription LAMBDA_NANJING '
                               '--remnant-mass-prescription FRYER2012 --fryer-supernova-engine DELAYED '
                               '--mass-transfer-angular-momentum-loss-prescription ISOTROPIC '
                               '--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 '
                              '--')
        self.output_dir = TemporaryDirectory()
        self.output_path = self.output_dir.name
        # self.detailed_output_path = os.path.join(self.output_dir.name, 'COMPAS_Output',
        #                                          'Detailed_Output', 'BSE_Detailed_Output_0.h5')
        # self.plotting_file_path = "./compasui/tests/test_data/BSE_Detailed_Output_0.h5"

        # self.detailed_plot_path = os.path.join(self.output_path, 'detailedEvolutionPlot.png')
        # self.vanDenHeuval_plot_path = os.path.join(self.output_path, 'vanDenHeuvalPlot.png')
        # self.evol_text_path = os.path.join(self.output_path, 'detailed_evol.txt')

    def tearDown(self):
        self.output_dir.cleanup()

    def test_run_compas_success(self):
        result = run_compas(self.parameter_str, self.output_path)
        self.assertEqual(result, TASK_SUCCESS)

    # @patch("compasui.tasks.run_compas_cmd")
    # def test_run_compas_failure(self, run_compas_cmd):
    #     run_compas_cmd.side_effect = Exception('something went wrong')
    #     result = run_compas(self.parameter_str, self.detailed_output_path)
    #     self.assertEqual(result, TASK_FAIL)
    #
    # @patch("compasui.tasks.run_compas_cmd")
    # def test_run_compas_timeout(self, run_compas_cmd):
    #     run_compas_cmd.side_effect = SoftTimeLimitExceeded
    #     result = run_compas(self.parameter_str, self.detailed_output_path)
    #     self.assertEqual(result, TASK_TIMEOUT)
