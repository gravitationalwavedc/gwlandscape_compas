import React, { memo } from 'react';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import ExponentTick from './ExponentTick';
import useZoomableDomain from './useZoomableDomain';
import PlotLineZoom from './PlotLineZoom';

const SingleBinaryPlot = memo(function RenderPlot({ data }) {
    const {
        meta: { xAxis, yAxis },
        groups,
        refLines,
        texts,
    } = data;
    const { isZoomed, xTicks, yTicks, xDomain, yDomain, ...handlers } = useZoomableDomain({ xAxis, yAxis });
    const xLabel = xAxis.label.reduce((label, token) => label + token[1], '');
    const yLabel = yAxis.label.reduce((label, token) => label + token[1], '');
    const isLogX = xAxis.scale === 'log';
    const isLogY = yAxis.scale === 'log';

    return (
        <PlotLineZoom
            groups={groups}
            refLines={refLines}
            texts={texts}
            onZoomIn={handlers.handleZoomIn}
            onZoomOut={handlers.handleZoomOut}
            isZoomed={isZoomed}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                allowDataOverflow
                allowDuplicatedCategory={false}
                scale={xAxis.scale}
                domain={xDomain}
                dataKey="x"
                type="number"
                reversed={xAxis.inverted}
                ticks={xTicks}
                tickFormatter={isLogX ? null : (f) => f.toFixed(2)}
                tick={isLogX ? <ExponentTick /> : true}
            >
                <Label value={xLabel} position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                scale={yAxis.scale}
                domain={yDomain}
                type="number"
                reversed={yAxis.inverted}
                ticks={yTicks}
                tickFormatter={isLogY ? null : (f) => f.toFixed(2)}
                tick={isLogY ? <ExponentTick /> : true}
            >
                <Label value={yLabel} angle="-90" position="insideLeft" textAnchor="middle" offset="-5" />
            </YAxis>
            <Legend
                wrapperStyle={{ paddingLeft: '40px' }}
                layout="vertical"
                align="right"
                verticalAlign="top"
                iconType="plainline"
            />
        </PlotLineZoom>
    );
});

export default SingleBinaryPlot;
