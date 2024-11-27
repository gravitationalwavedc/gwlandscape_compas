import React, { useRef } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip, ReferenceLine, Customized } from 'recharts';
import useZoom from './useZoom';

const TestCustom = (props) => {
    console.log(props);
    return <></>;
};

const PlotLineZoom = ({
    syncId,
    data,
    meta,
    refLines,
    handleZoomIn,
    handleZoomOut,
    isZoomed,
    children,
    yunit,
}) => {
    const onZoomIn = ({x1, y1, x2, y2}) =>{
        const xKey = meta[0].xKey;
        const xrangeData = data.filter((p) => p[xKey] >= x1 && p[xKey] <= x2);
        const hasDataInRange = xrangeData.some((point) => {
            let datapoints = Object.values(point);
            return datapoints.some((p) => p >= y1 && p <= y2);
        });
        if (hasDataInRange) {
            handleZoomIn({x1, y1, x2, y2});
        }
    };

    const chartRef = useRef();

    const drawReferenceLine = ({ key, dashes, colour, points, width }) => <ReferenceLine
        key={key}
        stroke={colour}
        strokeWidth={width}
        strokeDasharray={dashes}
        segment={points}
    />;

    const {isZooming, zoomArea, handleMouseDown, handleMouseMove, handleMouseUp } = useZoom({onZoomIn, chartRef});

    const drawLine = ({ key, label, width, dashes, colour }) => (
        <Line
            id={key}
            dataKey={key}
            key={key}
            name={label}
            stroke={colour}
            strokeWidth={width}
            strokeDasharray={dashes}
            dot={false}
        />
    );

    return (
        <div style={{ width: '100%', height: '600px' }}>
            {isZoomed && <button onClick={handleZoomOut}>Zoom Out</button>}
            <ResponsiveContainer width="80%" height="100%">
                <LineChart
                    width={700}
                    height={300}
                    data={data}
                    syncId={syncId}
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
                    {meta.map((lineMeta) => drawLine(lineMeta))}
                    {isZooming && <ReferenceArea {...zoomArea}/>}
                    {refLines.map(refLine => drawReferenceLine(refLine))}
                    <Customized component={TestCustom}/>
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
