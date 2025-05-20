import React, { useRef, useState } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip, ReferenceLine, Customized } from 'recharts';
import useZoom from './useZoom';
import { filterGroupDataByDomain } from './Utils';


const drawLine = ({ meta, data }) => (
    <Line
        id={meta.yKey}
        data={data}
        dataKey={meta.yKey}
        key={meta.label}
        name={meta.label}
        stroke={meta.colour}
        strokeWidth={meta.width}
        strokeDasharray={meta.dashes}
        dot={false}
        isAnimationActive={false}
    />
);

const drawLineGroup = ({ meta, data }) => meta.map(lineMeta => drawLine({meta: lineMeta, data}));

const drawReferenceLine = ({ refLineMeta: {meta, data}, yAxisMap }) => {
    const {label, dashes, colour, width, type} = meta;
    const dataCopy = data.map(point => ({...point}));
    if (type === 'vline') {
        const yAxis = yAxisMap[0];
        const yRange = yAxis.scale.range();
        dataCopy[0].y = yAxis.scale.invert(dataCopy[0].y * (yRange[1] - yRange[0]) + yRange[0]);
        dataCopy[1].y = yAxis.scale.invert(dataCopy[1].y * (yRange[1] - yRange[0]) + yRange[0]);
    }
    return <ReferenceLine
        key={label}
        stroke={colour}
        strokeWidth={width}
        strokeDasharray={dashes}
        segment={dataCopy}
        ifOverflow='hidden'
    />;
};

const drawText = ({text: {meta, data}, xAxisMap, yAxisMap}) => {
    const {label, colour} = meta;
    const pixX = xAxisMap[0].scale(data.x);
    const pixY = yAxisMap[0].scale(data.y);
    return <text
        key={`${label}-${data.x}-${data.y}`}
        textAnchor='middle'
        fill={colour}
        x={pixX}
        y={pixY}
    >
        {
            label.map(token => {
                if (token[0] === 'text') {
                    return <tspan key={token[1]}>{token[1]}</tspan>;
                } else if (token[0] === 'subscript') {
                    return <React.Fragment key={token[1]}>
                        <tspan dy={6}>{token[1]}</tspan>
                        <tspan dy={-6}>&#8203;</tspan>
                    </React.Fragment>;
                } else if (token[0] === 'superscript') {
                    return <React.Fragment key={token[1]}>
                        <tspan dy={-6}>{token[1]}</tspan>
                        <tspan dy={6}>&#8203;</tspan>
                    </React.Fragment>;
                }
            })
        }
    </text>;
};


const PlotLineZoom = ({
    syncId,
    groups: initialGroups,
    refLines,
    texts,
    onZoomIn: handleZoomIn,
    onZoomOut: handleZoomOut,
    isZoomed,
    children,
    yunit,
}) => {
    const [groups, setGroups] = useState(initialGroups);

    const onZoomIn = (domain) => {
        const filteredGroups = initialGroups.map(group => filterGroupDataByDomain(group, domain));
        setGroups(filteredGroups);
        handleZoomIn(domain);
    };

    const onZoomOut = () => {
        setGroups(initialGroups);
        handleZoomOut();
    };

    const chartRef = useRef();

    const {isZooming, zoomArea, handleMouseDown, handleMouseMove, handleMouseUp } = useZoom({onZoomIn, chartRef});

    // We split into cases with one group vs multiple groups for the sake of speed
    // Having multiple groups seems to slow things down, but unfortunately seems to be the best way
    // to plot lines with different sets of x-values
    const hasLineGroups = groups && groups.length > 1;

    const drawLineGroups = (groups) => hasLineGroups
        ? groups.map(group => drawLineGroup(group))
        : groups[0].meta.map(lineMeta => drawLine({meta: lineMeta}));

    return (
        <div style={{ width: '100%', height: '600px' }}>
            {isZoomed && <button onClick={onZoomOut}>Zoom Out</button>}
            <ResponsiveContainer width="80%" height="100%">
                <LineChart
                    width={700}
                    height={300}
                    syncId={syncId}
                    data={!hasLineGroups && groups[0].data}
                    margin={{
                        top: 5,
                        right: 20,
                        left: 20,
                        bottom: 25,
                    }}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    ref={chartRef}
                >
                    {children}
                    {drawLineGroups(groups)}
                    {isZooming && <ReferenceArea {...zoomArea}/>}
                    {
                        refLines.map(
                            refLine => <Customized
                                key={refLine.meta.label} component={drawReferenceLine} refLineMeta={refLine}
                            />
                        )
                    }
                    {texts.map(text => <Customized key={text.meta.label} component={drawText} text={text}/>)}
                    <Tooltip
                        allowEscapeViewBox={{ x: true, y: false }}
                        offset={20}
                        formatter={(value) => (
                            <>
                                {value.toFixed(2)} {yunit}
                            </>
                        )}
                        labelFormatter={(label) => `Time : ${label.toFixed(2)} Myr`}
                        filterNull={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PlotLineZoom;
