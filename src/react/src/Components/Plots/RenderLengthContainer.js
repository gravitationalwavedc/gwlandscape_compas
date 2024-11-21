import React, { memo, useMemo } from 'react';
import { units, length, mapLineData, getMinMax } from './DataUtil';
import { tickExpFormatter } from './Utils';
import PlotLineZoom from './PlotLineZoom';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import ExponentTick from './ExponentTick';
import useZoomableDomain from './useZoomableDomain';

const RenderLengthContainer = memo(function RenderLengthContainer({ data, syncId }) {
    const aliases = {
        semimajor: 'semi-major axis',
        periapsis: 'periapsis',
        radius_1: 'radius 1',
        radius_2: 'radius 2',
        roche_radius_1: 'roche radius 1',
        roche_radius_2: 'roche radius 2',
        time: 'time',
    };

    const strokeStyle = {
        semimajor: { stroke: 'black', strokeWidth: '2' },
        periapsis: { stroke: 'black', strokeWidth: '2', strokeDasharray: '5 5' },
        radius_1: { stroke: 'red', strokeWidth: '2' },
        radius_2: { stroke: 'blue', strokeWidth: '2' },
        roche_radius_1: { stroke: 'red', strokeDasharray: '5 5', strokeWidth: '2' },
        roche_radius_2: { stroke: 'blue', strokeDasharray: '5 5', strokeWidth: '2' },
    };

    // 'time' is the xkey, the other aliases are the ykeys
    const { time: xkey, ...ykeys } = aliases;

    const dataset = length(data);
    const chartData = mapLineData(dataset);
    const [minMaxX, minMaxY] = useMemo(() => getMinMax(dataset, xkey, ykeys), []);

    const xScale = 'linear';
    const yScale = 'log';

    const {
        handleZoomIn, handleZoomOut, isZoomed, xTicks, yTicks, xDomain, yDomain
    } = useZoomableDomain({minMaxX, minMaxY, xScale, yScale});

    return (
        <PlotLineZoom
            syncId={syncId}
            data={chartData}
            xkey={xkey}
            ykeys={Object.keys(ykeys)}
            handleZoomIn={handleZoomIn}
            handleZoomOut={handleZoomOut}
            isZoomed={isZoomed}
            strokeStyle={strokeStyle}
            aliases={aliases}
            yunit={units._length}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                allowDataOverflow
                scale={xScale}
                type="number"
                domain={xDomain}
                dataKey={xkey}
                padding={{ left: 20 }}
                tickFormatter={(f) => f.toFixed(2)}
                ticks={xTicks}
            >
                <Label value="Time(Myr)" position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                scale={yScale}
                tickFormatter={tickExpFormatter}
                domain={yDomain}
                padding={{ bottom: 5, left: 10 }}
                tick={<ExponentTick />}
                ticks={yTicks}
            >
                <Label value={'Radius(R\u{2299})'} angle="-90" position="insideLeft" textAnchor="middle" offset="-5" />
            </YAxis>
            <Legend layout="vertical" align="right" verticalAlign="top" />
        </PlotLineZoom>
    );
});

export default RenderLengthContainer;
