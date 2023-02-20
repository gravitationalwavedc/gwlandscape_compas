import datetime
import json
import os

import jwt
import requests
from django.conf import settings
from django.db import transaction

from .models import CompasJob, Label, SingleBinaryJob, BasicParameter, AdvancedParameter
from .tasks import run_compas
from .utils.constants import TASK_FAIL, TASK_TIMEOUT


def create_compas_job(user, start, basic_parameters, advanced_parameters):

    with transaction.atomic():
        compas_job = CompasJob(
            user_id=user.user_id,
            name=start.name,
            description=start.description,
            private=start.private,
            is_ligo_job=False
        )
        compas_job.save()
        for name, value in basic_parameters.items():
            BasicParameter(job=compas_job, name=name, value=value).save()

        for name, value in advanced_parameters.items():
            AdvancedParameter(job=compas_job, name=name, value=value).save()

        # Submit the job to the job controller
        # Create the jwt token
        jwt_enc = jwt.encode(
            {
                'userId': user.user_id,
                'exp': datetime.datetime.now() + datetime.timedelta(days=30)
            },
            settings.JOB_CONTROLLER_JWT_SECRET,
            algorithm='HS256'
        )

        # Create the parameter json
        params = compas_job.as_json()

        # Construct the request parameters to the job controller, note that parameters must be a string, not an objects
        data = {
            "parameters": json.dumps(params),
            "cluster": "gwlandscape",
            "bundle": "05a07631d8efcd1f979e4c4c09fd9fcc4bc9a3a2"
        }

        # Initiate the request to the job controller
        result = requests.request(
            "POST", settings.GWCLOUD_JOB_CONTROLLER_API_URL + "/job/",
            data=json.dumps(data),
            headers={
                "Authorization": jwt_enc
            }
        )

        # Check that the request was successful
        if result.status_code != 200:
            # Oops
            msg = f"Error submitting job, got error code: {result.status_code}\n\n{result.headers}\n\n{result.content}"
            print(msg)
            raise Exception(msg)

        print(f"Job submitted OK.\n{result.headers}\n\n{result.content}")

        # Parse the response from the job controller
        result = json.loads(result.content)

        # Save the job id
        compas_job.job_controller_id = result["jobId"]
        compas_job.save()
        return compas_job


def update_compas_job(job_id, user, private=None, labels=None):
    compas_job = CompasJob.get_by_id(job_id, user)

    if user.user_id == compas_job.user_id:
        if labels is not None:
            compas_job.labels.set(Label.filter_by_name(labels))

        if private is not None:
            compas_job.private = private

        compas_job.save()

        return 'Job saved!'
    else:
        raise Exception('You must own the job to change the privacy!')


def create_single_binary_job(
            mass1, mass2, metallicity, eccentricity, separation, orbital_period,
            velocity_1, velocity_2,
            common_envelope_alpha, common_envelope_lambda_prescription,
            remnant_mass_prescription, fryer_supernova_engine,
            kick_velocity_distribution,
            mass_transfer_angular_momentum_loss_prescription,
            mass_transfer_accretion_efficiency_prescription, mass_transfer_fa):
    single_binary_job = SingleBinaryJob(
        mass1=mass1,
        mass2=mass2,
        metallicity=metallicity,
        eccentricity=eccentricity,
        separation=separation,
        orbital_period=orbital_period,
        velocity_1=velocity_1,
        velocity_2=velocity_2,
        common_envelope_alpha=common_envelope_alpha,
        common_envelope_lambda_prescription=common_envelope_lambda_prescription,
        remnant_mass_prescription=remnant_mass_prescription,
        fryer_supernova_engine=fryer_supernova_engine,
        kick_velocity_distribution=kick_velocity_distribution,
        mass_transfer_angular_momentum_loss_prescription=mass_transfer_angular_momentum_loss_prescription,
        mass_transfer_accretion_efficiency_prescription=mass_transfer_accretion_efficiency_prescription,
        mass_transfer_fa=mass_transfer_fa,
    )
    single_binary_job.save()
    model_id = str(single_binary_job.id)

    grid_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'BSE_grid.txt')
    output_path = os.path.join(settings.COMPAS_IO_PATH, model_id)
    detailed_output_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output',
                                             'Detailed_Output', 'BSE_Detailed_Output_0.h5')

    task = run_compas.delay(grid_file_path, output_path, detailed_output_file_path)

    # get task result
    result = task.get()

    if result in (TASK_FAIL, TASK_TIMEOUT):
        raise Exception(model_id)

    return single_binary_job
