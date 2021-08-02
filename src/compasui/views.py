import datetime
import json

import jwt
import requests
from django.conf import settings
from django.db import transaction

# from .forms import CompasJobForm
from .models import CompasJob, DataParameter, Label, SearchParameter, Data, Search


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
