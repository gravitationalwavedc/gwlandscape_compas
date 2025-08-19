import { memo } from 'react';
import { XAxis, YAxis, CartesianGrid, Legend, Label, Tooltip } from 'recharts';
import ExponentTick from './ExponentTick';
import useZoomableDomain from './useZoomableDomain';
import PlotLineZoom from './PlotLineZoom';

const CustomTooltip = ({ active, payload, label, xLabel, yLabel }) => {
    if (active && payload && payload.length) {
        return (
            <div className="border bg-white" style={{ opacity: 0.8 }}>
                <p className="px-1 py-0 my-0 font-weight-bold bg-light">{xLabel}</p>
                <hr className="w-75 my-0 p-0" />
                <p className="px-1 py-0 my-0">{label.toFixed(2)}</p>
                <p className="px-1 py-0 my-0 font-weight-bold bg-light border-top">{yLabel}</p>
                <hr className="w-75 my-0 p-0" />
                {payload.map(({ name, value, color }) => (
                    <p key={name} style={{ color: color }} className="px-1 py-0 my-0">
                        {`${name} : ${value.toFixed(2)}`}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

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
            <Tooltip
                allowEscapeViewBox={{ x: true, y: false }}
                offset={20}
                filterNull={false}
                content={CustomTooltip}
                xLabel={xLabel}
                yLabel={yLabel}
            />
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
