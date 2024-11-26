import React, { useState, memo, useMemo } from 'react';
import { mapLineData, units, mass, getMinMax, compareDomains } from './DataUtil';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import PlotLineZoom from './PlotLineZoom';
import { getTickMarks } from './tickHelper';

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

    const initialDomain = {
        x1: minMaxX[0],
        x2: minMaxX[1],
        y1: minMaxY[0],
        y2: minMaxY[1],
    };

    const [domain, setDomain] = useState(initialDomain);

    const isInitialDomain = compareDomains(domain, initialDomain);

    const xTicks = getTickMarks(domain.x1, domain.x2, 8, !isInitialDomain);
    const yTicks = getTickMarks(domain.y1, domain.y2, 5, !isInitialDomain);

    return (
        <PlotLineZoom
            syncId={syncId}
            data={chartData}
            xkey={xkey}
            ykeys={Object.keys(ykeys)}
            initialDomain={initialDomain}
            setDomain={setDomain}
            strokeStyle={strokeStyle}
            aliases={aliases}
            yunit={units.mass}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                allowDataOverflow
                type="number"
                domain={isInitialDomain ? [xTicks[0], xTicks[xTicks.length - 1]] : [domain.x1, domain.x2]}
                dataKey={xkey}
                padding={{ left: 20 }}
                tickFormatter={(f) => f.toFixed(2)}
                ticks={xTicks}
            >
                <Label value={`Time(${units.time})`} position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                domain={isInitialDomain ? [yTicks[0], yTicks[yTicks.length - 1]] : [domain.y1, domain.y2]}
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
