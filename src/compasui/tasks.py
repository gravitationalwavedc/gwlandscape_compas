from celery import shared_task

import os
import logging
import traceback
from pathlib import Path
from subprocess import call, run

from .utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
from celery.exceptions import SoftTimeLimitExceeded

# Configure logger
logger = logging.getLogger(__name__)


def check_output_file_generated(outputfilepath):
    """
    Check if the job finished successfully by checking that output file is created
    This will keep running until file is created or Celery raises SoftTimeLimitExceeded
    :param outputfilepath: full path of output file
    :return: TASK_SUCCESS if file exists
    """
    import time

    while True:
        if os.path.exists(outputfilepath):
            return TASK_SUCCESS
        time.sleep(0.5)  # Check every half second to reduce CPU usage

    # This will never be reached as Celery will raise SoftTimeLimitExceeded
    # when the time limit is exceeded


@shared_task
def run_compas(parameter_str, output_path):
    result = None
    try:
        git_directory = os.environ.get("COMPAS_ROOT_DIR")
        compas_executable = Path(git_directory) / "src/COMPAS"
        compas_command = (
            f"{compas_executable} --detailed-output --number-of-systems 1 "
            f"--output-path {output_path} {parameter_str}"
        )

        detailed_output_file_path = (
            f"{output_path}/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5"
        )

        call(compas_command, shell=True)
        result = check_output_file_generated(detailed_output_file_path)

    except SoftTimeLimitExceeded:
        logger.error("Task exceeded time limit", exc_info=True)
        result = TASK_TIMEOUT
    except Exception:
        # return fail code if job failed for some other reason
        logger.error("Task failed with exception", exc_info=True)
        result = TASK_FAIL
    finally:
        return result


@shared_task(soft_time_limit=300, time_limit=600)  # Set time limits for VIMES task
def run_vimes(job_output_dir, scaling="log", images="default"):
    result = None
    try:
        detailed_output_file_path = f"{job_output_dir}/BSE_Detailed_Output_0.h5"
        frames_file_path = f"{job_output_dir}/frames_data.npz"
        movie_file_path = f"{job_output_dir}/{scaling}_{images}_movie.mp4"

        if os.path.exists(movie_file_path):
            return TASK_SUCCESS

        if not os.path.exists(frames_file_path):
            run(
                f"vimes-preprocess {detailed_output_file_path} {frames_file_path}",
                shell=True,
                check=True,
            )

        if os.path.exists(frames_file_path):
            run(
                f"vimes {frames_file_path} --scaling {scaling} --images {images} --save-mp4 {movie_file_path} --no-display",
                shell=True,
                check=True,
            )

        result = check_output_file_generated(movie_file_path)

    except SoftTimeLimitExceeded:
        logger.error("Task exceeded time limit", exc_info=True)
        result = TASK_TIMEOUT
    except Exception:
        # return fail code if job failed for some other reason
        logger.error("Task failed with exception", exc_info=True)
        result = TASK_FAIL
    finally:
        return result
