// eslint-disable-next-line complexity
const wideFilter = (data, i, key, data1, data2) => {
    let next = null;
    let prev = null;
    let nextInRange = false;
    let prevInRange = false;
    if (i > 0 && i <= data.length - 1) {
        prev = data[i-1][key];
        prevInRange = prev >= data1 && prev <= data2;
    }
    if (i >= 0 && i < data.length - 1) {
        next = data[i+1][key];
        nextInRange = next >= data1 && next <= data2;
    }
    const rangeInPrevNext = (prev && next) && (prev <= data1 && data2 <= next);
    return prevInRange || nextInRange || rangeInPrevNext; 
};

const filterGroupDataByDomain = (group, domain) => {
    const { meta, data } = group;
    const { x1, y1, x2, y2 } = domain;
    const xKey = meta[0].xKey; // A group only uses one xKey
    const xRangeData = data.filter((_, i) => wideFilter(data, i, xKey, x1, x2));
    const filteredData = xRangeData.filter((point, j) => {
        let keys = Object.keys(point);
        return keys.some((key) => {
            if (key === xKey) return false;
            return wideFilter(xRangeData, j, key, y1, y2);
        });
    });
    return {
        meta: meta,
        data: filteredData
    };
};

export {filterGroupDataByDomain};
