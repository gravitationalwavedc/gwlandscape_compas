import traceback
import json
import h5py as h5

def read_h5_data_as_json(h5filepath):
    json_data = None
    try:
        data = h5.File(h5filepath, 'r')
        h5array = {key: data[key][...].tolist() for key in data.keys()}
        json_data = json.dumps(h5array)
        del data
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        return json_data
