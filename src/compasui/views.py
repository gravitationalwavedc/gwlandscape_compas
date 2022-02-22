import datetime
import json
import os

import jwt
import requests
from django.conf import settings
from django.db import transaction

# from .forms import CompasJobForm
from .models import CompasJob, DataParameter, Label, SearchParameter, Data, Search, SingleBinaryJob
from .tasks import run_compas, run_plotting, run_detailed_evol_plotting,test_task
from .utils.constants import TASK_SUCCESS, TASK_FAIL, TASK_TIMEOUT
def create_compas_job(user, start, data, data_parameters, search_parameters):
    # validate_form = CompasJobForm(data={**start, **data, **signal, **sampler})
    # should be making use of cleaned_data below

    # Right now, it is not possible to create a non-ligo job
    if not user.is_ligo:
        raise Exception("User must be ligo")

    with transaction.atomic():
        compas_job = CompasJob(
            user_id=user.user_id,
            name=start.name,
            description=start.description,
            private=start.private,
            is_ligo_job=True
        )
        compas_job.save()

        job_data = Data(
            job=compas_job,
            data_choice=data.data_choice,
            source_dataset=data.source_dataset
        )

        job_data.save()

        for key, val in data_parameters.items():
            DataParameter(job=compas_job, data=job_data, name=key, value=val).save()

        job_search = Search(
            job=compas_job,
        )

        job_search.save()

        for key, val in search_parameters.items():
            SearchParameter(job=compas_job, search=job_search, name=key, value=val).save()

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
            "cluster": "ozstar",
            "bundle": "0992ae26454c2a9204718afed9dc7b3d11d9cbf8"
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
        velocity_random_number_1, velocity_random_number_2,
        theta_1, theta_2, phi_1, phi_2, mean_anomaly_1, mean_anomaly_2,
        common_envelope_alpha, common_envelope_lambda_prescription, common_envelope_lambda,
        remnant_mass_prescription, fryer_supernova_engine, black_hole_kicks,
        kick_velocity_distribution, kick_velocity_sigma_CCSN_NS, kick_velocity_sigma_CCSN_BH,
        kick_velocity_sigma_ECSN, kick_velocity_sigma_USSN, pair_instability_supernovae,
        pisn_lower_limit, pisn_upper_limit, pulsational_pair_instability_supernovae,
        ppi_lower_limit, ppi_upper_limit, pulsational_pair_instability_prescription,
        maximum_neutron_star_mass, mass_transfer_angular_momentum_loss_prescription,
        mass_transfer_accertion_efficiency_prescription, mass_transfer_fa, mass_transfer_jloss
):
    single_binary_job = SingleBinaryJob(
        mass1=mass1,
        mass2=mass2,
        metallicity=metallicity,
        eccentricity=eccentricity,
        separation=separation,
        orbital_period=orbital_period,
        velocity_random_number_1=velocity_random_number_1,
        velocity_random_number_2=velocity_random_number_2,
        theta_1=theta_1,
        theta_2=theta_2,
        phi_1=phi_1,
        phi_2=phi_2,
        mean_anomaly_1=mean_anomaly_1,
        mean_anomaly_2=mean_anomaly_2,
        common_envelope_alpha=common_envelope_alpha,
        common_envelope_lambda_prescription=common_envelope_lambda_prescription,
        common_envelope_lambda=common_envelope_lambda,
        remnant_mass_prescription=remnant_mass_prescription,
        fryer_supernova_engine=fryer_supernova_engine,
        black_hole_kicks=black_hole_kicks,
        kick_velocity_distribution=kick_velocity_distribution,
        kick_velocity_sigma_CCSN_NS=kick_velocity_sigma_CCSN_NS,
        kick_velocity_sigma_CCSN_BH=kick_velocity_sigma_CCSN_BH,
        kick_velocity_sigma_ECSN=kick_velocity_sigma_ECSN,
        kick_velocity_sigma_USSN=kick_velocity_sigma_USSN,
        pair_instability_supernovae=pair_instability_supernovae,
        pisn_lower_limit=pisn_lower_limit,
        pisn_upper_limit=pisn_upper_limit,
        pulsational_pair_instability_supernovae=pulsational_pair_instability_supernovae,
        ppi_lower_limit=ppi_lower_limit,
        ppi_upper_limit=ppi_upper_limit,
        pulsational_pair_instability_prescription=pulsational_pair_instability_prescription,
        maximum_neutron_star_mass=maximum_neutron_star_mass,
        mass_transfer_angular_momentum_loss_prescription=mass_transfer_angular_momentum_loss_prescription,
        mass_transfer_accertion_efficiency_prescription=mass_transfer_accertion_efficiency_prescription,
        mass_transfer_fa=mass_transfer_fa,
        mass_transfer_jloss=mass_transfer_jloss,
    )
    single_binary_job.save()
    model_id = str(single_binary_job.id)

    grid_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'BSE_grid.txt')
    output_path = os.path.join(settings.COMPAS_IO_PATH, model_id)
    detailed_output_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output','Detailed_Output', 'BSE_Detailed_Output_0.h5')
    detailed_plot_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output','Detailed_Output', 'detailedEvolutionPlot.png')
    vanDenHeuval_plot_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output','Detailed_Output', 'vanDenHeuvalPlot.png')
    evol_text_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output','Detailed_Output', 'detailed_evol.txt')

    # run compas as a Celery task
    task = run_compas.apply_async((grid_file_path, output_path, detailed_output_file_path),
                                  link=run_detailed_evol_plotting.s(detailed_output_file_path, detailed_plot_path, vanDenHeuval_plot_path, evol_text_path))
    # get task result
    result = task.get()
    if result in (TASK_FAIL, TASK_TIMEOUT):
        raise Exception(model_id);

    return single_binary_job