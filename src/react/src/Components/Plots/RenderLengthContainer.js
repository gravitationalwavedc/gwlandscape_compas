import React, { useState, memo } from 'react';
import { length, mapLineData } from './DataUtil';
import { tickExpFormatter } from './Utils';
import PlotLineZoom from './PlotLineZoom';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Legend,
    Label
} from 'recharts';

const RenderLengthContainer = memo(function RenderLengthContainer({ data, syncId }) {
    const [domain, setDomain] = useState({
        x1: 'auto',
        x2: dataMax => (dataMax * 1.1),
        y1: 'auto',
        y2: 'dataMax+1000'
    });

    const chartData = mapLineData(length(data));

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

    const adjustDomain = (area) => {
        setDomain(() => ({ x1: area.x1, x2: area.x2, y1: area.y1, y2: area.y2 }));
    };

    // 'time' is the xkey, the other aliases are the ykeys
    const { time: xkey, ...ykeys } = aliases;

    return (<PlotLineZoom
        syncId={syncId}
        data={chartData}
        xkey={xkey}
        ykeys={Object.keys(ykeys)}
        initialState={domain}
        adjustDomain={adjustDomain}
        strokeStyle={strokeStyle}
        aliases={aliases}
        scaleType='Log'
        yunit={<>R<sub>&#8857;</sub></>} >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
            allowDataOverflow
            type="number"
            scale='time'
            domain={[domain.x1, domain.x2]}
            dataKey={xkey}
            padding={{ left: 20 }}
            unit=""
            tickFormatter={f => f.toFixed(2)}>
            <Label value="Time(Myr)" position="bottom" offset={0} />
        </XAxis>
        <YAxis
            allowDataOverflow
            scale='log'
            tickFormatter={tickExpFormatter}
            domain={[domain.y1, domain.y2]}
            padding={{ bottom: 5 }}
            label={{ 
                value: 'Radius(R\u{2299})',
                angle: -90,
                position: 'insideLeft',
                textAnchor: 'middle',
                offset: -5 
            }} />
        <Legend layout="vertical" align="right" verticalAlign="top" />
    </PlotLineZoom>);
});

export default RenderLengthContainer;
