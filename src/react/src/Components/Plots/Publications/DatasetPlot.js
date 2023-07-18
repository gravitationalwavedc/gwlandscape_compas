import React from 'react';
import {
    interpolateViridis,
    interpolateCividis,
    interpolateMagma,
    interpolateInferno,
    interpolateSpectral
} from 'd3-scale-chromatic';
import {
    ReferenceArea,
    ReferenceLine,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ResponsiveContainer,
    Tooltip,
    ZAxis
} from 'recharts';
import { logString, formatAxis, getColourbarData, getTickMarks } from './Utils';
import CustomTooltip from './CustomTooltip';

const NUM_TICKS = 6;

const colourScales = {
    'viridis': interpolateViridis,
    'cividis': interpolateCividis,
    'magma': interpolateMagma,
    'inferno': interpolateInferno,
    'spectral': interpolateSpectral
};

// Can't really help complexity in Recharts, because you can't really make reusable components
// I could move all the logic to other functions, but it would
// just clutter the code with heaps of effectively useless functions
/* eslint-disable complexity */
const DatasetPlot = ({
    histData,
    minMaxX,
    minMaxY,
    logCheckX,
    logCheckY,
    nullCheckX,
    nullCheckY,
    sides,
    scatterData,
    axis,
    colourMap,
}) => {
    const ticksX = getTickMarks(minMaxX[0], minMaxX[1], NUM_TICKS);
    const ticksY = getTickMarks(minMaxY[0], minMaxY[1], NUM_TICKS);

    const plotMinX = ticksX[0];
    const plotMaxX = ticksX[ticksX.length-1];
    const plotMinY = ticksY[0];
    const plotMaxY = ticksY[ticksY.length-1];

    const cb = getColourbarData(histData, [plotMinX, plotMaxX], [plotMinY, plotMaxY], colourScales[colourMap]);

    return (
        <ResponsiveContainer width="100%" aspect={1.25} minWidth={500}>
            <ScatterChart
                width={500}
                height={500}
                margin={{
                    top: 30,
                    right: 130,
                    bottom: 130,
                    left: 80,
                }}
            >
                <XAxis
                    dataKey={'x'}
                    label={{
                        value: logString(axis[0], logCheckX),
                        position: 'insideBottomRight',
                        dx: 5,
                        dy: 20,
                        stroke: '#9E9E9E',
                        fontSize: 15,
                    }}
                    type="number"
                    ticks={nullCheckX ? ticksX.slice(1) : ticksX}
                    tick={{ fontSize: 13, transform: 'translate(0, 3)' }}
                    tickFormatter={formatAxis}
                    domain={[plotMinX, plotMaxX]}
                />
                <YAxis
                    dataKey={'y'}
                    label={{
                        value: logString(axis[1], logCheckY),
                        position: 'insideTopLeft',
                        angle: -90,
                        dx: -15,
                        dy: 0,
                        stroke: '#9E9E9E',
                        style: { textAnchor: 'end' },
                        fontSize: 15,
                    }}
                    type="number"
                    ticks={nullCheckY ? ticksY.slice(1) : ticksY}
                    tick={{ fontSize: 13, transform: 'translate(-3, 0)' }}
                    tickFormatter={formatAxis}
                    domain={[plotMinY, plotMaxY]}
                />
                <ZAxis zAxisId="standard" dataKey="counts" range={[15, 15]} />
                {
                    histData.length && <>

                        <ZAxis zAxisId="invis-z" dataKey="counts" range={[100, 100]} />
                        <ReferenceArea
                            key={'extra'}
                            x1={cb.x}
                            x2={cb.x}
                            y1={cb.y}
                            y2={cb.y}
                            ifOverflow="visible"
                            label={{
                                value: logString('COUNT'),
                                position: 'left',
                                angle: -90,
                                stroke: '#898989',
                                dx: -5,
                                opacity: 0.6,
                                fontSize: 12,
                            }}
                        />

                        {
                            cb.colourRange.map((sector, index) => (
                                <ReferenceArea
                                    key={`cb${index}`}
                                    x1={cb.x}
                                    x2={cb.x + cb.width}
                                    y1={cb.y - cb.cellHeight * ((cb.numCells - index) + 0.5)}
                                    y2={cb.y - cb.cellHeight * ((cb.numCells - index) - 0.5)}
                                    fill={cb.colourFn(sector)}
                                    fillOpacity={1}
                                    stroke="#dadada"
                                    strokeOpacity={0.3}
                                    ifOverflow="visible"
                                    label={{
                                        value: `${
                                            index == 0
                                                ? cb.countMin
                                                : index == cb.numCells
                                                    ? cb.countMax
                                                    : ''
                                        }`,
                                        stroke: '#898989',
                                        position: 'right',
                                        opacity: 0.8,
                                        dx: 0,
                                        fontSize: 10,
                                    }}
                                />
                            ))
                        }

                        {
                            histData.map((sector, index) => (
                                <ReferenceArea
                                    key={`hist${index}`}
                                    x1={sector.x - sides[0] / 2}
                                    x2={sector.x + sides[0] / 2}
                                    y1={sector.y - sides[1] / 2}
                                    y2={sector.y + sides[1] / 2}
                                    fill={cb.colourFn(Math.log10(sector.counts))}
                                    fillOpacity={1}
                                    stroke="#dadada"
                                    strokeOpacity={0.3}
                                    ifOverflow="extendDomain"
                                />
                            ))
                        }
                        <Scatter
                            data={histData}
                            zAxisId="invis-z"
                            fill="#dadada"
                            shape="square"
                            opacity={0.05}
                            ifOverflow="visible"
                        />
                    </>
                }
                <Tooltip
                    content={CustomTooltip}
                    zeroValX={nullCheckX && minMaxX[0] + sides[0] / 2}
                    zeroValY={nullCheckY && minMaxY[0] + sides[1] / 2}
                />

                <Scatter
                    data={scatterData}
                    zAxisId="standard"
                    fill={cb?.colourFn && cb.colourFn(0)}
                    shape="circle"
                    ifOverflow="visible"
                />
                {nullCheckX && (
                    <ReferenceLine
                        segment={[
                            { x: minMaxX[0] + sides[0] / 2, y: plotMinY },
                            { x: minMaxX[0] + sides[0] / 2, y: plotMaxY },
                        ]}
                        stroke="#bababa"
                        strokeOpacity={0.7}
                        strokeDasharray="4 6"
                        strokeWidth={2}
                        label={{
                            value: 'ZERO',
                            angle: -90,
                            position: 'top',
                            stroke: '#bababa',
                            opacity: 0.9,
                            dx: 4,
                            dy: -13,
                            fontSize: 10,
                        }}
                        ifOverflow="visible"
                    />
                )}

                {nullCheckY && (
                    <ReferenceLine
                        segment={[
                            { x: plotMinX, y: minMaxY[0] + sides[1] / 2 },
                            { x: plotMaxX, y: minMaxY[0] + sides[1] / 2 },
                        ]}
                        stroke="#bababa"
                        strokeOpacity={0.7}
                        strokeDasharray="4 6"
                        strokeWidth={2}
                        label={{
                            value: 'ZERO',
                            position: 'right',
                            stroke: '#bababa',
                            opacity: 0.9,
                            fontSize: 10,
                        }}
                        ifOverflow="visible"
                    />
                )}
                
            </ScatterChart>
        </ResponsiveContainer>
    );
};

export default DatasetPlot;