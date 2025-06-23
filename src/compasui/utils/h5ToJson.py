import traceback
import json
import h5py as h5
import numpy as np
import logging

# Set up a logger for this file
logger = logging.getLogger(__name__)


def read_h5_data_as_json(h5filepath):
    json_data = None
    data_dict = {}
    try:
        data = h5.File(h5filepath, "r")
        for key, dataset in data.items():
            # filter any nan, +inf, -inf values
            dataset = dataset[np.isfinite(dataset)]
            data_dict[key] = dataset.tolist()
        json_data = json.dumps(data_dict)
        del data
    except Exception as e:
        logger.error("Error reading H5 file: %s", h5filepath)
        raise e
    finally:
        return json_data
