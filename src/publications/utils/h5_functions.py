import numpy as np
import logging
from .plotting_functions import get_log_and_limits, histo2d_scatter_hybrid

# Set up a logger for this file
logger = logging.getLogger(__name__)

default_prefs = {
    "BSE_Common_Envelopes": ["SemiMajorAxis>CE", "SemiMajorAxis<CE"],
    "BSE_Double_Compact_Objects": ["Mass(1)", "Mass(2)"],
    "BSE_System_Parameters": ["Mass@ZAMS(1)", "Mass@ZAMS(2)"],
    "BSE_Supernovae": ["Mass(SN)", "Mass_CO_Core@CO(SN)"],
}


def get_h5_keys(h5_file):
    return list(h5_file.keys())


def get_h5_subgroups(h5_file, root_group):
    return get_h5_keys(h5_file[root_group])


def get_subgroup_units(h5_file, root_group, subgroup):
    units = h5_file[root_group][subgroup].attrs.get("units", b"-").decode("utf-8")

    if units in ["-", "State", "Event"]:
        return None

    return units


def check_subgroup_boolean(h5_file, root_group, subgroup):
    # Infer data to be boolean if it is unitless and the datatype is 8-bit int
    # Might need to add an extra check if this isn't stringent enough
    if get_subgroup_units(h5_file, root_group, subgroup) is not None:
        return False

    return h5_file[root_group][subgroup].dtype.type is np.uint8


def get_h5_subgroup_meta(h5_file, **kwargs):
    root_group = kwargs.pop("root_group", get_h5_keys(h5_file)[0])
    subgroup_list = get_h5_subgroups(h5_file, root_group)

    total_length = h5_file[root_group][subgroup_list[0]].shape[0]
    stride_length = 1 if total_length < 1e6 else int(total_length / 5e5)

    default_values = default_prefs.get(root_group, None)

    subgroup_x = kwargs.get(
        "subgroup_x", default_values[0] if default_values else subgroup_list[0]
    )
    subgroup_y = kwargs.get(
        "subgroup_y", default_values[1] if default_values else subgroup_list[1]
    )

    return {
        "groups": [key for key in get_h5_keys(h5_file) if key not in ["Run_Details"]],
        "group": root_group,
        "subgroups": subgroup_list,
        "subgroup_x": subgroup_x,
        "subgroup_y": subgroup_y,
        "subgroup_x_unit": get_subgroup_units(h5_file, root_group, subgroup_x),
        "subgroup_y_unit": get_subgroup_units(h5_file, root_group, subgroup_y),
        "stride_length": kwargs.get("stride_length", stride_length),
        "total_length": total_length,
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

    if data_group_x.dtype.type is np.bytes_ or data_group_y.dtype.type is np.bytes_:
        logger.warning("One of the subgroups has a dtype of string")
        return None

    data_group_x, data_group_y = remove_null_coords(data_group_x, data_group_y)

    # Check that the data is boolean
    bool_check_x = check_subgroup_boolean(h5_file, root_group, subgroup_x)
    bool_check_y = check_subgroup_boolean(h5_file, root_group, subgroup_y)

    # Check for log, get limits and flag if the minimum value is representing a log(0)
    data_group_x, log_check_x, min_max_x, null_check_x = get_log_and_limits(
        data_group_x, bool_check_x
    )
    data_group_y, log_check_y, min_max_y, null_check_y = get_log_and_limits(
        data_group_y, bool_check_y
    )
    plot_data = histo2d_scatter_hybrid(data_group_x, data_group_y, min_max_x, min_max_y)

    plot_data["min_max_x"] = min_max_x
    plot_data["min_max_y"] = min_max_y

    plot_data["null_check_x"] = null_check_x
    plot_data["null_check_y"] = null_check_y

    plot_data["log_check_x"] = log_check_x
    plot_data["log_check_y"] = log_check_y

    plot_data["bool_check_x"] = bool_check_x
    plot_data["bool_check_y"] = bool_check_y

    return plot_data


def remove_null_coords(x_array, y_array):
    # Select only points where both are not null
    null_indices = np.isfinite(x_array) & np.isfinite(y_array)
    return x_array[null_indices], y_array[null_indices]
