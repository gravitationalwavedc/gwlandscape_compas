import traceback
import json
import h5py as h5
import numpy as np


def read_h5_data_as_json(h5filepath):
    json_data = None
    data_dict = {}
    try:
        data = h5.File(h5filepath, 'r')
        for key in data.keys():
            dataset = data[key]
            dataset = dataset[~np.isnan(dataset)]
            data_dict[key] = dataset.tolist()
        json_data = json.dumps(data_dict)
        del data
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        return json_data
