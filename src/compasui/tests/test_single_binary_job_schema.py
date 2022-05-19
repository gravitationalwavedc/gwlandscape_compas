from os import path
from unittest.mock import patch
from django.conf import settings
from compasui.tests.testcases import CompasTestCase
from compasui.utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT


class TestSingleBinaryJobSchema(CompasTestCase):
    def setUp(self):

        self.create_single_binary_job_mutation = """
            mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
                newSingleBinary(input: $input) {
                    result {
                        jobId
                        gridFilePath
                        plotFilePath
                        vanPlotFilePath
                        detailedOutputFilePath
                    }
                }
            }
        """
        self.single_binary_job_input = {
            'input': {
                'mass1': 1.5,
                'mass2': 1.51,
                'metallicity': 0.02,
                'eccentricity': 0.1,
                'separation': 0.1,
                'meanAnomaly1': 0.1,
                'commonEnvelopeAlpha': 0.1,
                'commonEnvelopeLambdaPrescription': 'LAMBDA_FIXED',
                'commonEnvelopeLambda': 1.1,
                'ppiLowerLimit': 0.1,
                'pisnUpperLimit': 0.2,
                'fryerSupernovaEngine': 'DELAYED',
                'kickVelocityDistribution': 'ZERO',
                'pairInstabilitySupernovae': 'false',
                'pulsationalPairInstabilitySupernovae': 'true',
            }
        }

        self.expected_failed = {
            'newSingleBinary': {
                'result': {
                    'jobId': '',
                    'gridFilePath': '',
                    'plotFilePath': '',
                    'vanPlotFilePath': '',
                    'detailedOutputFilePath': ''
                }
            }
        }

    def test_new_single_binary_job_exception_no_redis_raised(self):
        print("Not mocking tasks or redis. Tasks fail as celery cannot connect to redis")
        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        expected = {
            'newSingleBinary': {
                'result': {
                    'jobId': '',
                    'gridFilePath': '',
                    'plotFilePath': '',
                    'vanPlotFilePath': '',
                    'detailedOutputFilePath': ''
                }
            }
        }
        self.assertEqual(expected, response.data)

    @patch('compasui.views.chain')
    @patch('compasui.views.run_compas')
    @patch('compasui.views.run_detailed_evol_plotting')
    def test_celery_tasks_called(self, run_detailed_evol_plotting, run_compas, chain):
        print("mocking celery task calls")

        run_compas.s.return_value = TASK_SUCCESS
        run_detailed_evol_plotting.s.return_value = TASK_FAIL

        self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        grid_file_path = path.join(settings.COMPAS_IO_PATH, '1', 'BSE_grid.txt')
        output_path = path.join(settings.COMPAS_IO_PATH, '1')
        detailed_output_file_path = path.join(settings.COMPAS_IO_PATH, '1', 'COMPAS_Output',
                                              'Detailed_Output', 'BSE_Detailed_Output_0.h5')
        detailed_plot_path = path.join(settings.COMPAS_IO_PATH, '1', 'COMPAS_Output',
                                       'Detailed_Output', 'detailedEvolutionPlot.png')
        vanDenHeuval_plot_path = path.join(settings.COMPAS_IO_PATH, '1', 'COMPAS_Output',
                                           'Detailed_Output', 'vanDenHeuvalPlot.png')
        evol_text_path = path.join(settings.COMPAS_IO_PATH, '1', 'COMPAS_Output',
                                   'Detailed_Output', 'detailed_evol.txt')

        run_compas.s.assert_called_with(grid_file_path, output_path, detailed_output_file_path)
        run_detailed_evol_plotting.s.assert_called_with(
            detailed_output_file_path, detailed_plot_path, vanDenHeuval_plot_path, evol_text_path)

        chain.assert_called_with(TASK_SUCCESS, TASK_FAIL)

    @patch('compasui.views.chain')
    def test_new_single_binary_mutation_when_tasks_fail(self, chain):
        print("mocking celery tasks failure")
        chain()().get.return_value = TASK_FAIL

        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        self.assertRaises(Exception, "1")
        self.assertEqual(self.expected_failed, response.data)

        chain()().get.return_value = TASK_TIMEOUT
        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )
        self.assertEqual(chain()().get.call_count, 2)
        self.assertEqual(self.expected_failed, response.data)

    @patch('compasui.views.chain')
    def test_new_single_binary_mutation_when_tasks_succeed(self, chain):
        print("mocking celery tasks success")

        plot_file_path = f'{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/detailedEvolutionPlot.png'
        grid_file_path = f'{settings.MEDIA_URL}jobs/1/BSE_grid.txt'
        van_plot_file_path = f'{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/vanDenHeuvalPlot.png'
        detailed_output_file_path = f'{settings.MEDIA_URL}jobs/1/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'

        chain()().get.return_value = TASK_SUCCESS

        response = self.client.execute(
            self.create_single_binary_job_mutation,
            self.single_binary_job_input
        )

        expected_success = {
            'newSingleBinary': {
                'result': {
                    'jobId': '1',
                    'gridFilePath': grid_file_path,
                    'plotFilePath': plot_file_path,
                    'vanPlotFilePath': van_plot_file_path,
                    'detailedOutputFilePath': detailed_output_file_path
                }
            }
        }
        chain()().get.assert_called_once()
        self.assertEqual(expected_success, response.data)
