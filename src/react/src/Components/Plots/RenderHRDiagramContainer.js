import React, { memo } from 'react';
import { XAxis, YAxis, CartesianGrid, Legend, Label } from 'recharts';
import ExponentTick from './ExponentTick';
import useZoomableDomain from './useZoomableDomain';
import PlotLineZoom from './PlotLineZoom';

const RenderHRDiagramContainer = memo(function RenderHRDiagram({ data }) {
    const {meta: {xAxis, yAxis}, groups, refLines} = data.plots.hr_plot;
    const {isZoomed, xTicks, yTicks, xDomain, yDomain, ...handlers} = useZoomableDomain({xAxis, yAxis});

    return (
        <PlotLineZoom
            groups={groups}
            refLines={refLines}
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
                name="Temperature"
                type="number"
                reversed={true} //uncomment later
                ticks={xTicks}
                tick={<ExponentTick />}
            >
                <Label value="Temperature(K)" position="bottom" offset={0} />
            </XAxis>
            <YAxis
                allowDataOverflow
                scale={yAxis.scale}
                domain={yDomain}
                name="Luminosity"
                type="number"
                ticks={yTicks}
                tick={<ExponentTick />}
                label={{
                    value: 'Luminosity/L\u{2299}',
                    angle: -90,
                    position: 'insideLeft',
                    textAnchor: 'middle',
                    offset: -7,
                }}
            />
            <Legend
                wrapperStyle={{ paddingLeft: '40px' }}
                layout="vertical"
                align="right"
                verticalAlign="top"
            />
        </PlotLineZoom>
    );
});

export default RenderHRDiagramContainer;
