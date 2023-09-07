from celery import shared_task

import os
import traceback
from pathlib import Path
from subprocess import call

from .utils.celery_pythonSubmit import run_compas_cmd
from .utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from celery.exceptions import SoftTimeLimitExceeded


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


# @shared_task
# def run_compas_old(grid_file_path, output_path, detailed_output_file_path):
#     result = None
#     try:
#         run_compas_cmd(grid_file_path, output_path)
#         result = check_output_file_generated(detailed_output_file_path)
#
#     except SoftTimeLimitExceeded:
#         traceback.print_exc()
#         result = TASK_TIMEOUT
#     except Exception:
#         # return fail code if job failed for some other reason
#         traceback.print_exc()
#         result = TASK_FAIL
#     finally:
#         return result

@shared_task
def run_compas(parameter_str, output_path):
    result = None
    try:
        git_directory = os.environ.get('COMPAS_ROOT_DIR')
        compas_executable = Path(git_directory) / 'src/COMPAS'
        compas_command = (f'{compas_executable} --detailed-output --number-of-systems 1 '
                          f'--output-path {output_path} {parameter_str}')

        detailed_output_file_path = f'{output_path}/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'

        print(compas_command)
        call(compas_command, shell=True)
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
