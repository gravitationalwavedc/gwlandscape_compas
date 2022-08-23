import json
import os

from core.misc import working_directory
from db import get_unique_job_id, update_job
from scheduler.slurm import slurm_submit


def submit_template(wk_dir, job_name):
    """
    This function returns the slurm script that submits all related scripts as jobs
    The slurm script is itself a job
    all subsequent sbatch are jobs as well
    all slurm job ids should be saved in slurm_ids file for future reference (see last 2 lines in the script)
    :param wk_dir:
    :param job_name:
    :return:
    """
    return f"""#!/bin/bash
    #SBATCH --time=00:10:00
    #SBATCH --output={wk_dir}/submit/{job_name}_slurm.out
    #SBATCH --error={wk_dir}/submit/{job_name}_slurm.err
    jid0=($(sbatch {wk_dir}/submit/{job_name}_test.sh))
    echo "jid0 ${{jid0[-1]}}" >> {wk_dir}/submit/slurm_ids"""


def test_script_template(wk_dir, job_name):
    return f"""#!/bin/bash
    #SBATCH --job-name={job_name}_test
    #SBATCH --account=oz979
    #SBATCH --ntasks=1
    #SBATCH --time=00:60:00
    #SBATCH --output={wk_dir}/test/{job_name}_test.out
    #SBATCH --error={wk_dir}/test/{job_name}_test.err

    srun hostname
    srun echo Hello World!!
    srun sleep 60"""


def submit(details, input_params):
    print("Submitting new job...")

    # Convert the job data to a json object
    input_params = json.loads(input_params)

    # create job working directory
    wk_dir = working_directory(details, input_params)
    os.makedirs(wk_dir, exist_ok=True)

    # change working directory to job directory
    os.chdir(wk_dir)

    job_name = input_params["name"]

    # create submit directory, where all slurm scripts exist
    submit_dir_name = "submit"
    submit_dir = os.path.join(wk_dir, submit_dir_name)
    os.makedirs(submit_dir, exist_ok=True)

    # create the directory where the actual job output exists
    os.makedirs(os.path.join(wk_dir, 'test'), exist_ok=True)

    # Write slurm scripts
    slurm_script = os.path.join(submit_dir, f'{job_name}_slurm.sh')
    with open(slurm_script, "w") as f:
        f.write(submit_template(wk_dir, job_name))

    test_script = os.path.join(submit_dir, f'{job_name}_test.sh')
    with open(test_script, "w") as f:
        f.write(test_script_template(wk_dir, job_name))

    # Actually submit the job
    submit_bash_id = slurm_submit(slurm_script, wk_dir)

    # If the job was not submitted, simply return. When the job controller does a status update, we'll detect that
    # the job doesn't exist and report an error
    if not submit_bash_id:
        return None

    # Create a new job to store details
    job = {
        'job_id': get_unique_job_id(),
        'submit_id': submit_bash_id,
        'working_directory': wk_dir,
        'submit_directory': submit_dir
    }

    # Save the job in the database
    update_job(job)

    # return the job id
    return job['job_id']
