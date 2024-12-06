import React, { useRef } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip, ReferenceLine } from 'recharts';
import useZoom from './useZoom';
import { groupHasDataInDomain } from './Utils';


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
    />
);

const drawLineGroup = ({ meta, data }) => meta.map(lineMeta => drawLine({meta: lineMeta, data}));

const drawReferenceLine = ({ label, dashes, colour, points, width }) => <ReferenceLine
    key={label}
    stroke={colour}
    strokeWidth={width}
    strokeDasharray={dashes}
    segment={points}
    ifOverflow='hidden'
/>;

const PlotLineZoom = ({
    syncId,
    groups,
    refLines,
    onZoomIn: handleZoomIn,
    onZoomOut: handleZoomOut,
    isZoomed,
    children,
    yunit,
}) => {
    const onZoomIn = (domain) => {
        const hasDataInDomain = groups.some(group => groupHasDataInDomain(group, domain));
        if (hasDataInDomain) {
            handleZoomIn(domain);
        }
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
            {isZoomed && <button onClick={handleZoomOut}>Zoom Out</button>}
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
                    {refLines.map(refLine => drawReferenceLine(refLine))}
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
