import React from 'react';
import { scaleSequential } from 'd3-scale';
import { range } from 'd3-array';
import {
    interpolateViridis,
    interpolateCividis,
    interpolateMagma,
    interpolateInferno,
    interpolateSpectral
} from 'd3-scale-chromatic';
import {
    ReferenceArea,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ResponsiveContainer,
    Tooltip,
    ZAxis
} from 'recharts';
import { createTicks, logString, formatAxis, getCountLimits } from './Utils';
import CustomTooltip from './CustomTooltip';

const AXIS_SCALE = 0.05;
const NUM_TICKS = 6;

const colourScales = {
    'viridis': interpolateViridis,
    'cividis': interpolateCividis,
    'magma': interpolateMagma,
    'inferno': interpolateInferno,
    'spectral': interpolateSpectral
};

const DatasetPlot = ({
    histData,
    minMaxX,
    minMaxY,
    logCheckX,
    logCheckY,
    sides,
    scatterData,
    axis,
    colourMap,
}) => {
    const diffRangeX = Math.abs(minMaxX[1] - minMaxX[0]) * AXIS_SCALE;
    const diffRangeY = Math.abs(minMaxY[1] - minMaxY[0]) * AXIS_SCALE;
    
    const plotMinX = Math.floor((minMaxX[0] - diffRangeX) * 10) / 10;
    const plotMaxX = Math.ceil((minMaxX[1] + diffRangeX) * 10) / 10;
    const plotMinY = Math.floor((minMaxY[0] - diffRangeY) * 10) / 10;
    const plotMaxY = Math.ceil((minMaxY[1] + diffRangeY) * 10) / 10;
    
    const ticksX = createTicks(plotMinX, plotMaxX, NUM_TICKS);
    const ticksY = createTicks(plotMinY, plotMaxY, NUM_TICKS);

    // Only want to calc these values if we're plotting a histogram
    if (histData.length) {
        var {countMin, countMax} = getCountLimits(histData);
        var cbX = plotMaxX + 2.25 * sides[0];
        var cbY = plotMaxY;
        var cbWidth = sides[0];
        var cbHeight = 0.4 * Math.abs(plotMaxY - plotMinY);
        var cbNumCells = 10;
        var cbCellHeight = cbHeight / cbNumCells;
        var colourRange = range(countMin, countMax * 1.001, (countMax - countMin) / cbNumCells);
        var colourFn = scaleSequential(colourScales[colourMap]).domain([countMin, countMax]);
    }

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
                    ticks={minMaxX[2] ? ticksX.slice(1) : ticksX}
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
                    ticks={minMaxY[2] ? ticksY.slice(1) : ticksY}
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
                            x1={cbX}
                            x2={cbX}
                            y1={cbY}
                            y2={cbY}
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
                            colourRange.map((sector, index) => (
                                <ReferenceArea
                                    key={`cb${index}`}
                                    x1={cbX}
                                    x2={cbX + cbWidth}
                                    y1={cbY - cbCellHeight * ((cbNumCells - index) + 0.5)}
                                    y2={cbY - cbCellHeight * ((cbNumCells - index) - 0.5)}
                                    fill={colourFn(sector)}
                                    fillOpacity={0.5}
                                    stroke="#dadada"
                                    strokeOpacity={0.3}
                                    ifOverflow="visible"
                                    label={{
                                        value: `${
                                            index == 0
                                                ? countMin
                                                : index == cbNumCells
                                                    ? countMax
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
                                    fill={colourFn(Math.log10(sector.counts))}
                                    fillOpacity={0.5}
                                    stroke="#dadada"
                                    strokeOpacity={0.3}
                                    ifOverflow="visible"
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
                <Tooltip content={CustomTooltip}/>

                <Scatter
                    data={scatterData}
                    zAxisId="standard"
                    fill="purple"
                    shape="circle"
                    ifOverflow="visible"
                />
                
            </ScatterChart>
        </ResponsiveContainer>
    );
};

export default DatasetPlot;