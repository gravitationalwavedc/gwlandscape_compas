import json
from .plotting_functions import data_query

def get_h5_keys(h5_file):
    return list(h5_file.keys())

def get_h5_subgroups(h5_file, root_group):
    return get_h5_keys(h5_file[root_group])

default_prefs = {
    'BSE_Common_Envelopes': ['SemiMajorAxis>CE', 'SemiMajorAxis<CE'],
    'BSE_Double_Compact_Objects': ['Mass(1)', 'Mass(2)'],
    'BSE_System_Parameters': ['Mass@ZAMS(1)', 'Mass@ZAMS(2)'],
    'BSE_Supernovae': ['Mass(SN)', 'Mass_CO_Core@CO(SN)']
}

def get_h5_subgroup_meta(h5_file, root_group):
    subgroup_list = get_h5_subgroups(h5_file, root_group)

    total_length = h5_file[root_group][subgroup_list[0]].shape[0]
    stride_length = 1 if total_length < 1e6 else total_length // 5e5

    # Ceiling division - apparently more accurate and faster than dividing and using math.ceil
    # https://stackoverflow.com/a/17511341
    file_length = -int(1.0 // -stride_length)

    default_values = default_prefs.get(root_group, None)

    initial_values = [
        subgroup_list.index(default_values[0]) if default_values else 0,
        subgroup_list.index(default_values[1]) if default_values else 1
    ]

    return json.dumps({
        "subgroupList": subgroup_list,
        "subgroupInit": initial_values,
        "numSamples": [file_length, total_length],
        "strideLength": stride_length,
    })

def get_h5_subgroup_data(h5_file, root_group, subgroup_x=None, subgroup_y=None, stride_length=1):
    default_values = default_prefs.get(root_group, None)
    if default_values and subgroup_x is None:
        subgroup_x = default_values[0]
    if default_values and subgroup_y is None:
        subgroup_y = default_values[1]
    
    total_length = h5_file[root_group][subgroup_x].shape[0]

    # Ceiling division - apparently more accurate and faster than dividing and using math.ceil
    # https://stackoverflow.com/a/17511341
    file_length = -int(1.0 // -stride_length)

    return json.dumps({
        "truncData": data_query(h5_file, root_group, subgroup_x, subgroup_y, stride_length),
        "numSamples": [file_length, total_length],
    })
