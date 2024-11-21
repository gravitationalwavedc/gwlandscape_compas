import React, { memo, useMemo } from 'react';
import { mapLineData, units, mass, getMinMax } from './DataUtil';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import PlotLineZoom from './PlotLineZoom';
import useZoomableDomain from './useZoomableDomain';

const RenderMassContainer = memo(function RenderMassContainer({ data, syncId }) {
    const aliases = {
        totalMass1: 'Mass1',
        totalMass2: 'Mass2',
        systemMass: 'System Mass',
        mass_CO_core1: 'CO core1',
        mass_CO_core2: 'CO core2',
        mass_HE_core1: 'HE core1',
        mass_HE_core2: 'HE core2',
        time: 'time',
    };

    const strokeStyle = {
        totalMass1: { stroke: 'red', strokeWidth: '2' },
        totalMass2: { stroke: 'blue', strokeWidth: '2' },
        systemMass: { stroke: 'black', strokeWidth: '2' },
        mass_CO_core1: { stroke: 'red', strokeDasharray: '5 5', strokeWidth: '2' },
        mass_CO_core2: { stroke: 'blue', strokeDasharray: '5 5', strokeWidth: '2' },
        mass_HE_core1: { stroke: 'red', strokeDasharray: '1 1 3', strokeWidth: '2' },
        mass_HE_core2: { stroke: 'blue', strokeDasharray: '1 1 3', strokeWidth: '2' },
    };

    // 'time' is the xkey, the other aliases are the ykeys
    const { time: xkey, ...ykeys } = aliases;

    const dataset = mass(data);
    const chartData = mapLineData(dataset);
    const [minMaxX, minMaxY] = useMemo(() => getMinMax(dataset, xkey, ykeys), []);

    const xScale = 'linear';
    const yScale = 'linear';

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
                <Label value={`Time(${units.time})`} position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                scale={yScale}
                domain={yDomain}
                padding={{ bottom: 5, left: 10 }}
                tickFormatter={(f) => f.toFixed(2)}
                ticks={yTicks}
            >
                <Label value={'Mass(M\u{2299})'} angle="-90" position="insideLeft" textAnchor="middle" offset="-5" />
            </YAxis>
            <Legend layout="vertical" align="right" verticalAlign="top" />
        </PlotLineZoom>
    );
});

export default RenderMassContainer;
