from pathlib import Path
import shutil

from django.conf import settings


def delete_previous_job_directory(curren_job_id):
    previous_job_dir = f'{settings.COMPAS_IO_PATH}{str(curren_job_id - 1)}'
    if Path(previous_job_dir).exists():
        shutil.rmtree(previous_job_dir)
