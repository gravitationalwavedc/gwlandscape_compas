import React from 'react';

const groupHasDataInDomain = (group, domain) => {
    const { meta, data } = group;
    const { x1, y1, x2, y2 } = domain;
    const xKey = meta[0].xKey; // A group only uses one xKey
    const xRangeData = data.filter((p) => p[xKey] >= x1 && p[xKey] <= x2);
    return xRangeData.some((point) => {
        let datapoints = Object.values(point);
        return datapoints.some((p) => p >= y1 && p <= y2);
    });
};

const filterScatterData = (data, xlabel, ylabel, x1, x2, y1, y2) =>
    data.filter((d) => d[xlabel] >= x1 && d[xlabel] <= x2 && d[ylabel] >= y1 && d[ylabel] <= y2);

const tickExpFormatter = (num) => {
    const superscript = '⁰¹²³⁴⁵⁶⁷⁸⁹';
    const minus = '⁻';

    const toSuper = (n) =>
        `${n}`
            .split('')
            .map((m) => (m === '-' ? minus : superscript[m]))
            .join('');

    const [base, exponent] = num
        .toExponential()
        .split('e')
        .map((n) => parseFloat(n));

    return base === 0 ? 0 : `${base === 1 ? '' : base.toFixed() + '×'}${10 + toSuper(exponent)}`;
};

const linspace = (start, stop, num, endpoint = true) => {
    const div = endpoint ? num - 1 : num;
    const step = (stop - start) / div;
    return Array.from({ length: num }, (_, i) => start + step * i);
};

const LineChartTooltip = (props) => {
    const { active, payload, label, xunit, yunit } = props;
    if (active && payload && payload.length) {
        return (
            <div>
                <p>{`${label} ${xunit}`}</p>
                {payload.map((p) => (
                    <p key={p.value}>
                        {`${p.value.toFixed(2)}`} {yunit}
                    </p>
                ))}
            </div>
        );
    }
};

const getLuminosity = (radius, temperature, Tsol = NaN) => {
    Tsol = Tsol || 6e3;
    temperature = temperature / Tsol;
    return radius ** 2 * temperature ** 4;
};

const getTemperature = (radius, luminosity, Tsol = NaN) => {
    Tsol = Tsol || 6e3;
    return (luminosity / radius ** 2) ** (1 / 4) * Tsol;
};

const getReferenceRangeType = (R, xDomain, yDomain) => {
    // returns 0 if out of bounds, 1 if left edge, 2 if right edge, 3 if both
    // 4 if outside on both edges but still crosses domain
    const Lmin = getLuminosity(R, xDomain[0]);
    const Lmax = getLuminosity(R, xDomain[1]);

    const edgeCheck = (checkNumber) => yDomain[0] < checkNumber && yDomain[1] > checkNumber;

    const left = edgeCheck(Lmin);
    const right = edgeCheck(Lmax);

    if ((yDomain[0] > Lmin && yDomain[1] < Lmax) || (yDomain[0] < Lmin && yDomain[1] > Lmax)) return 4;
    if (left && right) return 3;
    if (right) return 2;
    if (left) return 1;
    return 0;
};

const getReferenceLineSegment = (R, xDomain, yDomain) => {
    let rangeType = getReferenceRangeType(R, xDomain, yDomain);
    let segment = [];
    switch (rangeType) {
    case 1: //left edge
        segment = [
            { x: xDomain[0], y: getLuminosity(R, xDomain[0]) },
            { x: getTemperature(R, yDomain[1]), y: yDomain[1] },
        ];
        break;
    case 2: // right edge
        segment = [
            { x: getTemperature(R, yDomain[0]), y: yDomain[0] },
            { x: xDomain[1], y: getLuminosity(R, xDomain[1]) },
        ];
        break;
    case 3: // both edges
        segment = [
            { x: xDomain[0], y: getLuminosity(R, xDomain[0]) },
            { x: xDomain[1], y: getLuminosity(R, xDomain[1]) },
        ];
        break;
    case 4: // top and bottom edges
        segment = [
            { x: getTemperature(R, yDomain[0]), y: yDomain[0]},
            { x: getTemperature(R, yDomain[1]), y: yDomain[1]},
        ];
        break;
    default:
        return;
    }
    return segment;
};

export {
    filterScatterData as filterData,
    groupHasDataInDomain,
    tickExpFormatter,
    linspace,
    LineChartTooltip as CustomTooltip,
    getLuminosity,
    getTemperature,
    getReferenceLineSegment,
    getReferenceRangeType,
};
