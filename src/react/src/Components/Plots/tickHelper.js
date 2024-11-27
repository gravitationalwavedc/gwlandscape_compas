const getTickInterval = (minVal, maxVal, desiredNumTicks) => {
    // Approximate the tick interval by dividing the domain by desired tick number - 1
    const dataRange = Math.abs(maxVal - minVal);
    const approxTickInterval = dataRange / (desiredNumTicks - 1);

    // Rounds down to the nearest integer power of 10
    const orderOfMagnitude = Math.pow(10, Math.floor(Math.log10(dataRange)));

    // Scale tick interval to the order of magnitude before proceeding
    const scaledTickInterval = approxTickInterval / orderOfMagnitude;

    const magnitudes = [0.1, 0.25, 0.5, 1, 2, 5];
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

export const getTickMarks = (minVal, maxVal, numTicks) => {
    const tickInterval = getTickInterval(minVal, maxVal, numTicks);
    const startingPoint = Math.floor(minVal / tickInterval) * tickInterval;
    const tickMarks = [];
    for (var tick = startingPoint; tick < maxVal; tick += tickInterval) {
        tickMarks.push(tick);
    }
    tickMarks.push(tick);
    return tickMarks;
};

export const getLogTickMarks = (minVal, maxVal, numTicks) => {
    const ticks = getTickMarks(
        minVal > 0 ? Math.log10(minVal) : 0, maxVal > 0 ? Math.log10(maxVal) : 0, numTicks
    );
    return ticks.map((tick) => Math.pow(10, tick));
};

export const clampTicks = (minVal, maxVal, tickMarks) => tickMarks.filter(tick => tick >= minVal && tick <= maxVal);
