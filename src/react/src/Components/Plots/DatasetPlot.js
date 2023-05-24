import React from 'react';
import { scaleLinear } from 'd3-scale';
import { range } from 'd3-array';
import { format } from 'd3-format';
import {
    ReferenceArea,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ResponsiveContainer,
    ZAxis,
} from 'recharts';

const AXIS_SCALE = 0.05;
const NUM_TICKS = 6;

const formatAxis = (value) => {
    if (Math.abs(value) > 1e3) {
        return format('.1e')(value);
    }
    return format('.1f')(value);
};

const createTicks = (min, max, numTicks) => {
    const tickSteps = Math.abs(max - min) / numTicks;
    const axisRange = range(min, max * 1.01, tickSteps);
    return axisRange;
};

const DatasetPlot = ({ inpdata, axis }) => {
    const {histData, minmaxX, minmaxY, logCheckX, logCheckY, sides, scatterData} = inpdata;
    console.log(inpdata);

    const countMax = histData.reduce((a, b) => a.counts > b.counts ? a : b).counts;
    const countMin = histData.reduce((a, b) => a.counts < b.counts ? a : b).counts;

    const diffRangeX = Math.abs(minmaxX[1] - minmaxX[0]) * AXIS_SCALE;
    const diffRangeY = Math.abs(minmaxY[1] - minmaxY[0]) * AXIS_SCALE;

    const plotMinX = Math.floor((minmaxX[0] - diffRangeX) * 10) / 10;
    const plotMaxX = Math.ceil((minmaxX[1] + diffRangeX) * 10) / 10;
    const plotMinY = Math.floor((minmaxY[0] - diffRangeY) * 10) / 10;
    const plotMaxY = Math.ceil((minmaxY[1] + diffRangeY) * 10) / 10;

    const ticksX = createTicks(plotMinX, plotMaxX, NUM_TICKS);
    const ticksY = createTicks(plotMinY, plotMaxY, NUM_TICKS);

    const col = scaleLinear(
        [Math.log10(countMin), Math.log10(countMax)],
        ['purple', 'yellow']
    );

    return (
        <ResponsiveContainer width="85%" aspect={1} minWidth={500}>
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
                        value: logCheckX ? `log[${axis[0]}]` : axis[0],
                        position: 'insideBottomRight',
                        dx: 5,
                        dy: 20,
                        stroke: '#9E9E9E',
                        fontSize: 15,
                    }}
                    type="number"
                    ticks={minmaxX[2] ? ticksX.slice(1) : ticksX}
                    tick={{ fontSize: 13, transform: 'translate(0, 3)' }}
                    tickFormatter={formatAxis}
                    domain={[plotMinX, plotMaxX]}
                />
                <YAxis
                    dataKey={'y'}
                    label={{
                        value: logCheckY ? `log[${axis[1]}]` : axis[1],
                        position: 'insideTopLeft',
                        angle: -90,
                        dx: -15,
                        dy: 0,
                        stroke: '#9E9E9E',
                        style: { textAnchor: 'end' },
                        fontSize: 15,
                    }}
                    type="number"
                    ticks={minmaxY[2] ? ticksY.slice(1) : ticksY}
                    tick={{ fontSize: 13, transform: 'translate(-3, 0)' }}
                    tickFormatter={formatAxis}
                    domain={[plotMinY, plotMaxY]}
                />
                <ZAxis zAxisId="invis-z" dataKey="counts" range={[100, 100]} />
                <ZAxis zAxisId="standard" dataKey="counts" range={[15, 15]} />

                {
                    histData.map((sector, index) => (
                        <ReferenceArea
                            key={`hist${index}`}
                            x1={sector.x - sides[0] / 2}
                            x2={sector.x + sides[0] / 2}
                            y1={sector.y - sides[1] / 2}
                            y2={sector.y + sides[1] / 2}
                            fill={col(Math.log10(sector.counts))}
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