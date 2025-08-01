import json
import numpy as np
from itertools import product


def get_surrounding_bins(indices, x_lim, y_lim):
    """Given x and y indices, return the 3x3 indices surrounding the indices

    Parameters
    ----------
    indices : array_like
        List containing x and y indices
    x_lim : upp
        Upper x limit, beyond which indices should not be found
    y_lim : int
        Upper y limit, beyond which indices should not be found

    Returns
    -------
    array_like
        Array containing indices for the original indices and all surrounding in a 3x3 block,
        as long as they are within the limits
    """
    x, y = indices
    x1, x2 = max(x - 1, 0), min(x + 1, x_lim)
    y1, y2 = max(y - 1, 0), min(y + 1, y_lim)
    return np.array(list(product(range(x1, x2 + 1), range(y1, y2 + 1))))


def get_log_and_limits(arr, is_bool, max_cond=80, min_cond=1e-2):
    """Checks whether or not the input array should be logged,
    as well as returning sensible limits on the resulting array

    Parameters
    ----------
    arr : array_like
        Input 1D array to be logged
    max_cond : int or float, optional
        Log array if the maximum is above this value, by default 80
    min_cond : int or float, optional
        Log array if the minimum is below this value, by default 1e-2

    Returns
    -------
    array_like, bool, list
        Returns the array, a flag to show if it has been logged,
        and a list of sensible min and max values for the array when plotted
    """
    arr_max = float(np.max(arr))
    arr_min = float(np.min(arr))

    # If the data is boolean, we know what the limits should be
    # While the data will only be 0 or 1, we add a buffer on either side to make the plot look nicer
    if is_bool:
        return arr, False, [-0.5, 1.5], False

    # If the array minimum is lower than 0, shouldn't be logged
    if arr_min < 0:
        return arr, False, [arr_min, arr_max], False

    # If the array is uniform, log values if it is above or below a specific threshold, else leave
    if arr_max == arr_min:
        if min_cond < arr_max < max_cond or arr_max == 0:
            return arr, False, [arr_max - 0.01, arr_max + 0.01], False
        return (
            np.log10(arr),
            True,
            [np.log10(arr_max) - 0.01, np.log10(arr_max) + 0.01],
            False,
        )

    if min_cond < arr_max < max_cond:
        return arr, False, [arr_min, arr_max], False

    logged_arr = np.log10(arr)

    # If there are any negative infinites in the data, we replaced them with a value lower than the next lowest value
    # This will be used in plotting to display zeroes in a log plot
    if np.isinf(logged_arr).any():
        arr_min = np.min(arr[arr != 0])
        zero_value = np.log10(arr_min) - 0.25 * (np.log10(arr_max) - np.log10(arr_min))
        logged_arr = np.nan_to_num(logged_arr, neginf=zero_value)
        return logged_arr, True, [np.min(logged_arr), np.log10(arr_max)], True

    return logged_arr, True, [np.min(logged_arr), np.log10(arr_max)], False


def split_histogram_by_count(counts, split_count):
    """Takes the counts output of numpy.histogram2d and returns both the list of indices for counts
    over the split_count (and any bins surrounding these with any counts at all), and the list of
    indices for counts below the threshold, not included in the smoothed histogram bins

    Parameters
    ----------
    counts : array_like
        2D array of histogram bin counts
    split_count : int
        The threshold count at which the histogram bins will be split

    Returns
    -------
    tuple
        First index contains an array of the smoothed histogram indices, second index contains the remaining
        indices for bins with any counts at all
    """
    all_count_indices = np.array(np.where(counts > 0)).T
    min_count_indices = np.array(np.where(counts > split_count)).T

    x_lim, y_lim = counts.shape

    # Get all coordinates surrounding all histogram bins above split_count
    min_count_bins = [
        get_surrounding_bins(entry, x_lim=x_lim - 1, y_lim=y_lim - 1)
        for entry in min_count_indices
    ]

    if not len(min_count_bins):
        return np.array([]), all_count_indices

    smoothed_indices = np.concatenate(min_count_bins)

    # Remove doubles
    smoothed_indices = np.unique(smoothed_indices, axis=0)

    # For each of the coordinates, retain them only if they have any counts in them
    smoothed_unique_indices = smoothed_indices[
        np.asarray(
            [
                (entry == all_count_indices).all(axis=1).any()
                for entry in smoothed_indices
            ]
        )
    ]

    # Get the coordinates where there are counts, but not covered by smooth histogram
    inverse_unique_indices = all_count_indices[
        ~np.asarray(
            [
                (entry == smoothed_indices).all(axis=1).any()
                for entry in all_count_indices
            ]
        )
    ]

    return smoothed_unique_indices, inverse_unique_indices


def histo2d_scatter_hybrid(
    x_array, y_array, min_max_x, min_max_y, min_count=3, bins=40
):
    """Return data necessary to build a hybrid scatter-histogram plot

    Parameters
    ----------
    x_array : array-like
        Array of x-coordinates for each point
    y_array : array-like
        Array of y-coordinates for each point
    min_count : int, optional
        The minimum amount of counts in a histogram bin to be plotted, by default 3
    bins : int, optional
        The number of bins in each dimension, by default 40

    Returns
    -------
    dict
        Contains json data for the scatter plot and histogram, along with the side lengths of the histogram bins
    """
    # Small adjustment to the limits to force bins to fall on integer values if that's how the data are
    # This helps with displaying boolean data, and data for classifying stellar types etc.
    x_min, x_max = min_max_x
    y_min, y_max = min_max_y
    x_range, y_range = abs(x_max - x_min), abs(y_max - y_min)
    x_bins = round(round(bins / x_range) * x_range) if (bins / x_range > 1) else bins
    y_bins = round(round(bins / y_range) * y_range) if (bins / y_range > 1) else bins

    x_offset, y_offset = 0.5 * x_range / x_bins, 0.5 * y_range / y_bins
    x_limits = (x_min - x_offset, x_max + x_offset)
    y_limits = (y_min - y_offset, y_max + y_offset)
    counts, x_edges, y_edges = np.histogram2d(
        x_array, y_array, bins=(x_bins + 1, y_bins + 1), range=(x_limits, y_limits)
    )

    x_centers = (x_edges[1:] + x_edges[:-1]) / 2.0
    y_centers = (y_edges[1:] + y_edges[:-1]) / 2.0
    x_side, y_side = np.abs(x_edges[1] - x_edges[0]), np.abs(y_edges[1] - y_edges[0])

    histogram_indices, scatter_indices = split_histogram_by_count(counts, min_count)

    hist_json = [
        {"x": x_centers[xi], "y": y_centers[yi], "counts": counts[xi, yi]}
        for xi, yi in histogram_indices
    ]

    # Now to grab the scatter points of < min_count
    index_array = np.any(
        [
            np.logical_and(
                np.abs(x_array - x_centers[entry[0]]) <= x_side / 2.0,
                np.abs(y_array - y_centers[entry[1]]) <= y_side / 2.0,
            )
            for entry in scatter_indices
        ],
        axis=0,
    )

    scatter_json = [
        {"x": float(x), "y": float(y)}
        for x, y in np.column_stack((x_array, y_array))[index_array]
    ]

    return {
        "sides": [x_side, y_side],
        "hist_data": json.dumps(hist_json),
        "scatter_data": json.dumps(scatter_json),
    }
