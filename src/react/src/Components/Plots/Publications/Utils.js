import { format } from 'd3-format';
import { scaleSequential } from 'd3-scale';
import { range } from 'd3-array';

const formatAxis = (value, isBool) => {
    if (isBool) {
        return !!value ? 'True' : 'False'
    }
    return Math.abs(value) >= 1e3 ? format('.1e')(value) : format('.2~f')(value)
};

const logString = (str, isLog=true) => isLog ? `log[${str}]` : str;

const getCountLimits = (histData, isLog=true) => {
    let countMax = histData.reduce((a, b) => a.counts > b.counts ? a : b).counts;
    let countMin = histData.reduce((a, b) => a.counts < b.counts ? a : b).counts;

    countMax = isLog ? Math.log10(countMax) : countMax;
    countMin = isLog ? Math.log10(countMin) : countMin;

    countMax = Math.ceil(countMax * 10) / 10;
    countMin = Math.floor(countMin * 10) / 10;
    return {countMin, countMax};
};

const getColourbarData = (histData, xDomain, yDomain, colourScale) => {
    // Only want to calc these values if we're plotting a histogram
    if (histData.length) {
        const {countMin, countMax} = getCountLimits(histData);
        const x = xDomain[1] + 0.05 * Math.abs(xDomain[1] - xDomain[0]);
        const y = yDomain[1];
        const width = 0.025 * Math.abs(xDomain[1] - xDomain[0]);
        const height = 0.4 * Math.abs(yDomain[1] - yDomain[0]);
        const numCells = 10;
        const cellHeight = height / numCells;
        const colourRange = range(countMin, countMax * 1.001, (countMax - countMin) / numCells);
        const colourFn = scaleSequential(colourScale).domain([countMin, countMax]);
        return {countMin, countMax, x, y, width, height, numCells, cellHeight, colourRange, colourFn};
    }
    return null;
};

const getTickInterval = (minVal, maxVal, desiredNumTicks) => {
    // Approximate the tick interval by dividing the domain by desired tick number - 1
    const dataRange = Math.abs(maxVal - minVal);
    const approxTickInterval = dataRange / (desiredNumTicks - 1);

    // Rounds down to the nearest integer power of 10
    const orderOfMagnitude = Math.pow(10, Math.floor(Math.log10(dataRange)));

    // Scale tick interval to the order of magnitude before proceeding
    const scaledTickInterval = approxTickInterval / orderOfMagnitude;

    const magnitudes = [0.1,0.25,0.5,1,2,5];
    let tickInterval = magnitudes[0];
    let minDifference = Number.POSITIVE_INFINITY;

    // Check which magnitude is closest to the scaledTickInterval
    // which will be most likely to give the desired number of ticks
    // and then set tickInterval by rescaling magnitude by the orderOfMagnitude
    for (const magnitude of magnitudes) {
        const difference = Math.abs(scaledTickInterval - magnitude);
        if (difference < minDifference) {
            tickInterval = magnitude * orderOfMagnitude;
            minDifference = difference;
        }
    }
    
    return tickInterval;
};

const getTickMarks = (minVal, maxVal, numTicks) => {
    const tickInterval = getTickInterval(minVal, maxVal, numTicks);
    const startingPoint = Math.floor(minVal / tickInterval) * tickInterval;
    const tickMarks = [];
    for (var tick = startingPoint; tick < maxVal; tick += tickInterval){
        tickMarks.push(tick);
    }
    tickMarks.push(tick);
    return tickMarks;
};

export {formatAxis, logString, getCountLimits, getTickMarks, getColourbarData };