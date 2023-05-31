import json
import numpy as np

def smooth_histogram(arr, limx, limy):
    '''
    Component to look for adjacent indices. Used to smooth out histogram by including low-count bins adjacent to high-count bins
    '''
    arr_list = []
    x = arr[0]
    y = arr[1]
    
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if x+i < 0: continue
            if y+j < 0: continue
            if x+i > limx: continue
            if y+j > limy: continue
            arr_list.append([x+i, y+j])
            
    return np.asarray(arr_list)

def log_check(arr, max_cond=80, min_cond=1e-2):
    '''
    Log the array, replace -inf with the minimum non log(0) value + offset by a bit.
    This is done because it is incredibly likely that if the array is to be logged, that a '0' quantity means that it's null/off.
    We would like to use this to distinguish these quantities in the plot
    Replace infs with 1.79e308
    Return: data array (logged or not), 0/1 to indicate log status, Array(2) or Array(3) to indicate minmax with/without null
    '''
    arr = np.nan_to_num(arr, posinf=1.79e308, neginf=-1.79e308)
    arr_max = float(np.max(arr))
    arr_min = float(np.min(arr))

    log_arr_max = np.log10(arr_max)
    log_arr_min = np.log10(arr_min)

    # If the array minimum is lower than 0, it is likely a parameter and shouldn't be logged
    if arr_min < 0:
        return arr, 0, [arr_min, arr_max]

    # If the array is uniform, log values if it is above or below a specific threshold, else leave
    if arr_max == arr_min:
        if arr_max != 0 and (arr_max > max_cond or arr_min < min_cond):
            return np.log10(arr), 1, [arr_max - 0.5, arr_max + 0.5]
        return arr, 0, [arr_max - 0.5, arr_max + 0.5]

    if arr_max > max_cond or arr_max < min_cond:
        # If any of the logged array is infinite or NaN
        if (~np.isfinite(np.log10(arr))).any():
            arr_min = np.min(arr[arr != 0])            
            if arr_max:
                min_allowed_value = np.log10(arr_min) - 0.25 * (np.log10(arr_max) - np.log10(arr_min))
            else:
                min_allowed_value = np.log10(arr_min) - 1

            arr = np.nan_to_num(np.log10(arr), neginf=min_allowed_value)
            return arr, 1, [np.min(arr), np.log10(arr_max), np.log10(arr_min)]
        else:
            arr = np.log10(arr)
            return arr, 1, [np.min(arr), np.log10(arr_max)]

    return arr, 0, [arr_min, arr_max]

def histo2d_scatter_hybrid(arr, min_cnt=3, bins=40):
    '''
    Hybrid Histo + Scatter plot
    '''

    counts, x_edges, y_edges = np.histogram2d(arr[:,0], arr[:,1], bins=bins)

    x_centers = (x_edges[1:] + x_edges[:-1])/2.
    y_centers = (y_edges[1:] + y_edges[:-1])/2.
    x_side, y_side = np.abs(x_edges[1] - x_edges[0]), np.abs(y_edges[1] - y_edges[0])

    all_count_indices = np.array(np.where(counts > 0)).T
    min_count_indices = np.array(np.where(counts > min_cnt)).T
    min_count_expand = np.array([])

    for entry in min_count_indices:
        tmp_expand = smooth_histogram(entry, limx=bins-1, limy=bins-1)
        min_count_expand = np.concatenate((min_count_expand, tmp_expand)) if min_count_expand.size else tmp_expand

    min_count_expand = np.unique(min_count_expand, axis=0)

    min_count_unique = min_count_expand[np.asarray([(entry == all_count_indices).all(axis=1).any() for entry in min_count_expand])]
    inv_count_unique = all_count_indices[~np.asarray([(entry == min_count_expand).all(axis=1).any() for entry in all_count_indices])]

    hist_json = [{} for i in range(len(min_count_unique))]

    for idx, entry in enumerate(hist_json):
        x_idx = min_count_unique[idx][0]
        y_idx = min_count_unique[idx][1]

        entry['x'] = x_centers[x_idx]
        entry['y'] = y_centers[y_idx]
        entry['counts'] = counts[x_idx, y_idx]

    #Now to grab the scatter points of < min_cnt

    scatter_json = [{} for i in range(int(np.sum(counts[tuple(inv_count_unique.T)])))]
    running_count = 0

    for entry in inv_count_unique:
        tmp_arr_x = arr[(np.abs(arr[:,0] - x_centers[entry[0]]) <= x_side/2.)]
        tmp_arr = tmp_arr_x[(np.abs(tmp_arr_x[:,1] - y_centers[entry[1]]) <= y_side/2.)]
        
        for array in tmp_arr:
            scatter_json[running_count]['x'] = float(array[0])
            scatter_json[running_count]['y'] = float(array[1])
            running_count += 1

    return {
        'sides': [x_side, y_side],
        'hist_data': json.dumps(hist_json),
        'scatter_data': json.dumps(scatter_json)
    }
