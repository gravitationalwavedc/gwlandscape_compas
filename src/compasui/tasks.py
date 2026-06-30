import json
import logging
import os
import traceback
from itertools import chain
from pathlib import Path
from subprocess import call, run

import matplotlib
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

matplotlib.use("agg")
from compas_python_utils.detailed_evolution_plotter.plot_to_json import (
    get_plot_json,
)  # noqa: E402

from .utils.constants import TASK_FAIL, TASK_SUCCESS, TASK_TIMEOUT

# Configure logger
logger = logging.getLogger(__name__)


@shared_task
def run_compas(parameters, output_path):
    git_directory = os.environ.get("COMPAS_ROOT_DIR")

    compas_executable = Path(git_directory) / "src" / "COMPAS"

    detailed_output_path = Path(output_path) / "COMPAS_Output" / "Detailed_Output"
    output_file = detailed_output_path / "BSE_Detailed_Output_0.h5"
    json_file = detailed_output_path / "plot_data.json"

    compas_command = [
        str(compas_executable),
        "--detailed-output",
        "--number-of-systems",
        "1",
        "--output-path",
        str(output_path),
    ]
    compas_command.extend(map(str, chain.from_iterable(parameters.items())))

    try:
        completed = run(
            compas_command,
            capture_output=True,
            text=True,
            check=False,
        )

        if completed.returncode != 0:
            raise Exception(f"COMPAS exited with code {completed.returncode}")

        if not output_file.exists():
            raise Exception(f"Expected output file not found: {output_file}")

        json_data = get_plot_json(str(output_file))
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        if not json_file.exists():
            raise Exception(f"Expected json file not found: {json_file}")

        return str(output_file), str(json_file)

    except SoftTimeLimitExceeded:
        logger.exception("COMPAS task exceeded soft time limit")
        raise

    except Exception:
        logger.exception("COMPAS task failed")
        raise

    finally:
        import matplotlib.pyplot as plt

        plt.close("all")


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
