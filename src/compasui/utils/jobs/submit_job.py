import datetime
import json

import jwt
import requests
from django.conf import settings


def submit_job(params, user_id):
    # Create the jwt token
    jwt_enc = jwt.encode(
        {
            'userId': user_id,
            'exp': datetime.datetime.now() + datetime.timedelta(days=30)
        },
        settings.JOB_CONTROLLER_JWT_SECRET,
        algorithm='HS256'
    )

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

    # Return the job id
    return result["jobId"]