from celery import shared_task

from django.conf import settings

import os
import traceback
import importlib.util

from .utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from celery.exceptions import SoftTimeLimitExceeded

# get COMPAS directory
_compas_dir = os.environ['COMPAS_ROOT_DIR']

# load <_compas_dir>/utils/preProcessing/runSubmit.py module
_run_submit_spec = importlib.util.spec_from_file_location(
    'runSubmit',
    os.path.join(_compas_dir, 'utils', 'preProcessing', 'runSubmit.py')
)
_run_submit_module = importlib.util.module_from_spec(_run_submit_spec)
_run_submit_spec.loader.exec_module(_run_submit_module)


# load <_compas_dir>/utils/plot_detailed_evolution.py module
_plotting_spec = importlib.util.spec_from_file_location(
    'plot_detailed_evolution',
    os.path.join(_compas_dir, 'utils', 'plot_detailed_evolution.py')
)
_plotting_module = importlib.util.module_from_spec(_plotting_spec)
_plotting_spec.loader.exec_module(_plotting_module)


def check_output_file_generated(outputfilepath):
    """
    Check if the job finished successfully by checking that output file is created
    This will keep running until file is created or timeout otherwise
    :param outputfilepath: full path of output file
    :return:
    """
    created = False
    # keep checking until output file is generated
    while not created:
        created = os.path.exists(outputfilepath)

    return TASK_SUCCESS


@shared_task
def run_compas(grid_file_path, output_path, detailed_output_file_path):
    result = None
    try:
        # run_compas_cmd(grid_file_path, output_path)
        _run_submit_module.run_compas_command(
            configFileName=settings.COMPAS_CONFIG_PATH,
            gridFileName=grid_file_path,
            outputPath=output_path)

        result = check_output_file_generated(detailed_output_file_path)

    except SoftTimeLimitExceeded:
        traceback.print_exc()
        result = TASK_TIMEOUT
    except Exception:
        # return fail code if job failed for some other reason
        traceback.print_exc()
        result = TASK_FAIL
    finally:
        return result


@shared_task
def run_detailed_evol_plotting(jobstate, detailed_output_file_path,
                               detailed_plot_path, vanDenHeuval_plot_path, evol_text_path):

    if jobstate == TASK_SUCCESS:

        result = None
        try:
            _plotting_module.main(
                detailed_output_file_path,
                detailed_plot_path,
                vanDenHeuval_plot_path,
                evol_text_path)
            result = check_output_file_generated(vanDenHeuval_plot_path)
        except SoftTimeLimitExceeded:
            traceback.print_exc()
            result = TASK_TIMEOUT
        except Exception:
            traceback.print_exc()
            result = TASK_FAIL
        finally:
            return result

    elif jobstate == TASK_FAIL or jobstate == TASK_TIMEOUT:
        print("COMPAS Model didn't run successfully! Couldn't generate plot")
        return TASK_FAIL
