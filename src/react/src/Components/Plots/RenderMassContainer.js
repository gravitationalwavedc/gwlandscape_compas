import React, { useState, memo } from 'react';
import { mapLineData, units, mass } from './DataUtil';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import PlotLineZoom from './PlotLineZoom';

const initialDomain = { x1: 'auto', x2: (dataMax) => dataMax * 1.1, y1: 'auto', y2: 'dataMax' };

const RenderMassContainer = memo(function RenderMassContainer({ data, syncId }) {
    const [domain, setDomain] = useState(initialDomain);

    const mapData = mapLineData(mass(data));

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

    const xkey = 'time';
    const ykeys = Object.keys(aliases).filter((key) => key !== 'time');

    const adjustDomain = (area) => {
        setDomain(() => ({ x1: area.x1, x2: area.x2, y1: area.y1, y2: area.y2 }));
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

    return (
        <PlotLineZoom
            syncId={syncId}
            data={mapData}
            xkey={xkey}
            ykeys={ykeys}
            initialState={initialDomain}
            adjustDomain={adjustDomain}
            strokeStyle={strokeStyle}
            aliases={aliases}
            scaleType="Linear"
            yunit={units.mass}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                allowDataOverflow
                type="number"
                scale="time"
                domain={[domain.x1, domain.x2]}
                dataKey={xkey}
                padding={{ left: 20 }}
                unit=""
                tickFormatter={(f) => f.toFixed(2)}
            >
                <Label value={`Time(${units.time})`} position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                domain={[domain.y1, domain.y2]}
                padding={{ bottom: 5, left: 10 }}
                tickFormatter={(f) => f.toFixed(2)}
            >
                <Label value={'Mass(M\u{2299})'} angle="-90" position="insideLeft" textAnchor="middle" offset="-5" />
            </YAxis>
            <Legend layout="vertical" align="right" verticalAlign="top" />
        </PlotLineZoom>
    );
});

export default RenderMassContainer;
