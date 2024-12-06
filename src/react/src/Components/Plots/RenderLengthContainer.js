import React, { memo } from 'react';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import { units } from './DataUtil';
import { tickExpFormatter } from './Utils';
import PlotLineZoom from './PlotLineZoom';
import useZoomableDomain from './useZoomableDomain';
import ExponentTick from './ExponentTick';

const RenderLengthContainer = memo(function RenderLengthContainer({ data, syncId }) {
    const {meta: {xAxis, yAxis}, groups, refLines} = data.plots.length_plot;
    const {isZoomed, xTicks, yTicks, xDomain, yDomain, ...handlers} = useZoomableDomain({xAxis, yAxis});

    return (
        <PlotLineZoom
            syncId={syncId}
            groups={groups}
            refLines={refLines}
            onZoomIn={handlers.handleZoomIn}
            onZoomOut={handlers.handleZoomOut}
            isZoomed={isZoomed}
            yUnit={units._length}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                allowDataOverflow
                scale={xAxis.scale}
                type="number"
                domain={xDomain}
                dataKey="x"
                padding={{ left: 20 }}
                tickFormatter={(f) => f.toFixed(2)}
                ticks={xTicks}
            >
                <Label value="Time(Myr)" position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                scale={yAxis.scale}
                domain={yDomain}
                padding={{ bottom: 5, left: 10 }}
                tick={<ExponentTick />}
                tickFormatter={tickExpFormatter}
                ticks={yTicks}
            >
                <Label value={'Radius(R\u{2299})'} angle="-90" position="insideLeft" textAnchor="middle" offset="-5" />
            </YAxis>
            <Legend layout="vertical" align="right" verticalAlign="top" iconType="plainline" />
        </PlotLineZoom>
    );
});

export default RenderLengthContainer;
