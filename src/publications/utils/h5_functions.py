from .plotting_functions import get_log_and_limits, histo2d_scatter_hybrid

default_prefs = {
    'BSE_Common_Envelopes': ['SemiMajorAxis>CE', 'SemiMajorAxis<CE'],
    'BSE_Double_Compact_Objects': ['Mass(1)', 'Mass(2)'],
    'BSE_System_Parameters': ['Mass@ZAMS(1)', 'Mass@ZAMS(2)'],
    'BSE_Supernovae': ['Mass(SN)', 'Mass_CO_Core@CO(SN)']
}


def get_h5_keys(h5_file):
    return list(h5_file.keys())


def get_h5_subgroups(h5_file, root_group):
    return get_h5_keys(h5_file[root_group])


def get_h5_subgroup_meta(h5_file, root_group):
    subgroup_list = get_h5_subgroups(h5_file, root_group)

    total_length = h5_file[root_group][subgroup_list[0]].shape[0]
    stride_length = 1 if total_length < 1e6 else int(total_length // 5e5)

    default_values = default_prefs.get(root_group, None)

    return {
        "groups": get_h5_keys(h5_file),
        "group": root_group,
        "subgroups": subgroup_list,
        "subgroup_x": default_values[0] if default_values else subgroup_list[0],
        "subgroup_y": default_values[1] if default_values else subgroup_list[1],
        "stride_length": stride_length,
    }


def get_h5_subgroup_data(h5_file, root_group, subgroup_x, subgroup_y, stride_length=1):
    """Takes a H5 file and returns the data necessary for a histogram-scatter plot

    Parameters
    ----------
    h5_file : h5py.File
        H5 file containing the necessary data
    root_group : str
        The base group of the H5 file
    subgroup_x : str
        Subgroup for the x axis
    subgroup_y : str
        subgroup for the y axis
    stride_length : int, optional
        Will use obtain a subset of the data by striding at this interval, by default 1

    Returns
    -------
    dict
        Dictionary with the required data and metadata
    """
    data_group_x = h5_file[root_group][subgroup_x][::stride_length]
    data_group_y = h5_file[root_group][subgroup_y][::stride_length]

    # Check for log
    data_group_x, log_check_x, min_max_x = get_log_and_limits(data_group_x)
    data_group_y, log_check_y, min_max_y = get_log_and_limits(data_group_y)

    plot_data = histo2d_scatter_hybrid(data_group_x, data_group_y)

    plot_data['min_max_x'] = min_max_x
    plot_data['min_max_y'] = min_max_y

    plot_data['log_check_x'] = log_check_x
    plot_data['log_check_y'] = log_check_y

    return plot_data
