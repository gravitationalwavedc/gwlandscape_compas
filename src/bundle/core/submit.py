import json
import os
import shutil
from pathlib import Path
import yaml

from core.misc import working_directory
from _bundledb import create_or_update_job
from scheduler.slurm import slurm_submit


params_to_compas_commands = {
    'number_of_systems': '--number-of-systems',
    'min_initial_mass': '--initial-mass-min',
    'max_initial_mass': '--initial-mass-max',
    'initial_mass_function': '--initial-mass-function',
    'initial_mass_power': '--initial-mass-power',
    'min_metallicity': '--metallicity-min',
    'max_metallicity': '--metallicity-max',
    'metallicity_distribution': '--metallicity-distribution',
    'min_mass_ratio': '--mass-ratio-min',
    'max_mass_ratio': '--mass-ratio-max',
    'mass_ratio_distribution': '--mass-ratio-distribution',
    'min_semi_major_axis': '--semi-major-axis-min',
    'max_semi_major_axis': '--semi-major-axis-max',
    'semi_major_axis_distribution': '--semi-major-axis-distribution',
    'min_orbital_period': '--orbital-period-min',
    'max_orbital_period': '--orbital-period-max',
    'mass_transfer_angular_momentum_loss_prescription': '--mass-transfer-angular-momentum-loss-prescription',
    'mass_transfer_accretion_efficiency_prescription': '--mass-transfer-accretion-efficiency-prescription',
    'mass_transfer_fa': '--mass-transfer-fa',
    'common_envelope_alpha': '--common-envelope-alpha',
    'common_envelope_lambda_prescription': '--common-envelope-lambda-prescription',
    'remnant_mass_prescription': '--remnant-mass-prescription',
    'fryer_supernova_engine': '--fryer-supernova-engine',
    'kick_velocity_distribution': '--kick-magnitude-distribution',
    'velocity_1': '--kick-magnitude-1',
    'velocity_2': '--kick-magnitude-2'
}

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
#SBATCH --output={wk_dir}/submit/{job_name}_master_slurm.out
#SBATCH --error={wk_dir}/submit/{job_name}_master_slurm.err
jid0=($(sbatch {wk_dir}/submit/{job_name}_compas.sh))
echo "jid0 ${{jid0[-1]}}" >> {wk_dir}/submit/slurm_ids
jid1=($(sbatch --dependency=afterok:${{jid0[-1]}} {wk_dir}/submit/{job_name}_combineh5.sh))
echo "jid1 ${{jid1[-1]}}" >> {wk_dir}/submit/slurm_ids
"""


def compas_run_template(wk_dir, job_name, no_of_nodes):
    return f"""#!/bin/bash
#SBATCH --job-name={job_name}_compas
#SBATCH --array=1-{no_of_nodes}
#SBATCH --account=oz979
#SBATCH --ntasks=1
#SBATCH --output={wk_dir}/compas/run%a/{job_name}_compas_%a.out
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=0-001:00:00
#SBATCH --mem-per-cpu=16G
#SBATCH --tmp=8G

# Load modules
module load gcc/6.4.0
module load openmpi/3.0.0
module load boost/1.66.0-python-3.6.4
module load gsl/2.4
module load h5py/2.7.1-python-3.6.4-serial
module load numpy/1.14.1-python-3.6.4
module load pandas/0.22.0-python-3.6.4
module load astropy/3.1.2-python-3.6.4
module load scipy/1.0.0-python-3.6.4
module load pyyaml/3.12-python-3.6.4
BOOST_DIR='/apps/skylake/modulefiles/all/mpi/gcc/6.4.0/openmpi/3.0.0/boost/1.66.0-python-3.6.4.lua'
GSL_DIR='/apps/skylake/modulefiles/all/compiler/gcc/6.4.0/gsl/2.4.lua'

# Run python submit
cd {wk_dir}/compas/run${{SLURM_ARRAY_TASK_ID}}
srun python {wk_dir}/compas/run${{SLURM_ARRAY_TASK_ID}}/runSubmit_${{SLURM_ARRAY_TASK_ID}}.py \
>& {job_name}_${{SLURM_ARRAY_TASK_ID}}.log
"""


def combine_output_template(wk_dir, job_name):
    return f"""#!/bin/bash
#SBATCH --account=oz979
#SBATCH --job-name={job_name}_combineh5
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=0-001:00:00
#SBATCH --output={wk_dir}/compas/{job_name}_combineh5.out
#SBATCH --mem-per-cpu=16G
#SBATCH --tmp=8G


# Load modules
module load gcc/6.4.0
module load openmpi/3.0.0
module load boost/1.66.0-python-3.6.4
module load gsl/2.4
module load h5py/2.7.1-python-3.6.4-serial
module load numpy/1.14.1-python-3.6.4
module load pandas/0.22.0-python-3.6.4
module load astropy/3.1.2-python-3.6.4
module load scipy/1.0.0-python-3.6.4
module load pyyaml/3.12-python-3.6.4

# Run h5copy
cd {wk_dir}/compas
srun python /fred/oz979/GWLandscape/COMPAS/utils/h5copy.py input {wk_dir} -r
"""


def get_string_value(value):
    return value if value != '' else None


def get_numerical_value(value):
    return float(value) if value != '' else None


def read_default_yaml_config(yaml_file_path):
    with open(yaml_file_path) as f:
        config = yaml.load(f, yaml.Loader)
        return config


def update_yaml_config(default_config, input_params):
    params = {**input_params['basic'], **input_params['advanced']}

    for name, value in params.items():
        try:
            command = params_to_compas_commands[name]
            if command in default_config['stringChoices'].keys():
                default_config['stringChoices'][command] = get_string_value(value)
            elif command in default_config['booleanChoices'].keys():
                default_config['booleanChoices'][command] = bool(value)
            elif command in default_config['numericalChoices'].keys():
                default_config['numericalChoices'][command] = get_numerical_value(value)
            else:
                print(f'option {command} cannot be found in compas commands')
        except KeyError as e:
            print(e)
            continue

    return default_config


def submit(details, input_params):
    print("Submitting new job...")

    # Convert the job data to a json object
    input_params = json.loads(input_params)

    # create job working directory
    wk_dir = working_directory(details, input_params)
    Path(wk_dir).mkdir(parents=True, exist_ok=True)

    # change working directory to job directory
    os.chdir(wk_dir)

    job_name = input_params["name"]

    # create submit directory, where all slurm scripts exist
    submit_dir_name = "submit"
    submit_dir = Path(wk_dir) / submit_dir_name
    Path(submit_dir).mkdir(parents=True, exist_ok=True)

    # create the directory where the actual job output exists
    compas_dir = Path(wk_dir) / 'compas'
    Path(compas_dir).mkdir(parents=True, exist_ok=True)

    YAMLCONFIGPATH = "/fred/oz979/GWLandscape/COMPAS/utils/preProcessing/compasConfigDefault.yaml"

    default_yaml_config = read_default_yaml_config(YAMLCONFIGPATH)
    updated_yaml_config = update_yaml_config(default_yaml_config, input_params)

    no_of_systems = input_params["basic"]["number_of_systems"]
    no_of_nodes = 1
    PYTHONSUBMITPATH = '/fred/oz979/GWLandscape/COMPAS/utils/preProcessing/runSubmit.py'

    nsys_per_patch = int(no_of_systems) / int(no_of_nodes)
    nsys_remainder = int(no_of_systems) % int(no_of_nodes)

    # setup runs directories
    for i in range(no_of_nodes):
        run_dir = f'{wk_dir}/compas/run{i+1}'
        Path(run_dir).mkdir()
        shutil.copyfile(PYTHONSUBMITPATH, Path(run_dir) / f'runSubmit_{i+1}.py')

        nsysi = nsys_per_patch if i < no_of_nodes else nsys_per_patch + nsys_remainder
        updated_yaml_config['numericalChoices']['--number-of-systems'] = int(nsysi)

        with open(Path(run_dir) / 'compasConfigDefault.yaml', 'w') as yaml_file:
            yaml.dump(updated_yaml_config, yaml_file)

        start_seed = (i+1) * nsys_per_patch
        seed_file = Path(run_dir) / 'randomSeed.txt'
        with open(seed_file, 'w') as f:
            f.write(str(start_seed))

    # Write slurm scripts
    slurm_script = Path(wk_dir) / 'submit' / f'{job_name}_slurm.sh'
    with open(slurm_script, "w") as f:
        f.write(submit_template(wk_dir, job_name))

    compas_script = Path(wk_dir) / 'submit' / f'{job_name}_compas.sh'
    with open(compas_script, "w") as f:
        f.write(compas_run_template(wk_dir, job_name, no_of_nodes))

    combine_script = Path(wk_dir) / 'submit' / f'{job_name}_combineh5.sh'
    with open(combine_script, "w") as f:
        f.write(combine_output_template(wk_dir, job_name))

    # Actually submit the job
    submit_bash_id = slurm_submit(slurm_script, wk_dir)

    # If the job was not submitted, simply return. When the job controller does a status update, we'll detect that
    # the job doesn't exist and report an error
    if not submit_bash_id:
        return None

    # Create a new job to store details
    job = {
        'job_id': 0,
        'submit_id': submit_bash_id,
        'working_directory': wk_dir,
        'submit_directory': submit_dir_name
    }

    # Save the job in the database
    create_or_update_job(job)

    # return the job id
    return job['job_id']
