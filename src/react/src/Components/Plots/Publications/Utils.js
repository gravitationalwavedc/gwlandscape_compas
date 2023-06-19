import { range } from 'd3-array';
import { format } from 'd3-format';

const formatAxis = (value) => Math.abs(value) >= 1e3 ? format('.1e')(value) : format('.1f')(value);

const logString = (str, isLog=true) => isLog ? `log[${str}]` : str;

const createTicks = (min, max, numTicks) => {
    const tickSteps = Math.abs(max - min) / numTicks;
    const axisRange = range(min, max, tickSteps);
    axisRange.push(max);
    return axisRange;
};

const getCountLimits = (histData, isLog=true) => {
    let countMax = histData.reduce((a, b) => a.counts > b.counts ? a : b).counts;
    let countMin = histData.reduce((a, b) => a.counts < b.counts ? a : b).counts;

    countMax = isLog ? Math.log10(countMax) : countMax;
    countMin = isLog ? Math.log10(countMin) : countMin;

    countMax = Math.ceil(countMax * 10) / 10;
    countMin = Math.floor(countMin * 10) / 10;
    return {countMin, countMax};
};

export {formatAxis, logString, createTicks, getCountLimits};