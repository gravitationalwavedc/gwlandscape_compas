import React, { memo } from 'react';
import { units } from './DataUtil';
import { tickExpFormatter } from './Utils';
import PlotLineZoom from './PlotLineZoom';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import ExponentTick from './ExponentTick';
import useZoomableDomain from './useZoomableDomain';

const RenderLengthContainer = memo(function RenderLengthContainer({ data, syncId }) {
    const {meta: {xAxis, yAxis}, lines, refLines} = data.plots.length_plot;

    const {
        handleZoomIn, handleZoomOut, isZoomed, xTicks, yTicks, xDomain, yDomain
    } = useZoomableDomain({xAxis, yAxis});

    return (
        <PlotLineZoom
            syncId={syncId}
            data={lines.data}
            meta={lines.meta}
            refLines={refLines}
            handleZoomIn={handleZoomIn}
            handleZoomOut={handleZoomOut}
            isZoomed={isZoomed}
            yunit={units._length}
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
