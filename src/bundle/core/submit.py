import json

from core.utils.submit_multi import submit_multi
from core.utils.submit_single import submit_single


def submit(details, input_params):
    print("Submitting new job...")

    # Convert the job data to a json object
    input_params = json.loads(input_params)

    if input_params['type'] == 'single':
        return submit_single(details, input_params)
    elif input_params['type'] == 'multi':
        return submit_multi(details, input_params)
    else:
        print(f"Unknown job type: {input_params['type']}")
        raise
