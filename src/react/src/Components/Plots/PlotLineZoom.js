import React, { useRef } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip } from 'recharts';
import useZoom from './useZoom';

const PlotLineZoom = ({
    syncId,
    data,
    xkey,
    ykeys,
    handleZoomIn,
    handleZoomOut,
    isZoomed,
    strokeStyle,
    aliases,
    children,
    yunit,
}) => {
    const onZoomIn = ({x1, y1, x2, y2}) =>{
        const xrangeData = data.filter((p) => p[xkey] >= x1 && p[xkey] <= x2);
        const hasDataInRange = xrangeData.some((point) => {
            let datapoints = Object.values(point);
            return datapoints.some((p) => p >= y1 && p <= y2);
        });
        if (hasDataInRange) {
            handleZoomIn({x1, y1, x2, y2});
        }
    };

    const chartRef = useRef();

    const {isZooming, zoomArea, handleMouseDown, handleMouseMove, handleMouseUp } = useZoom({onZoomIn, chartRef});

    const drawLine = (dataKey, alias = null, style, type = null, dot = false) => {
        if (dataKey === 'time') return;
        return (
            <Line
                id={dataKey}
                type={type || 'monotone'}
                dataKey={dataKey}
                key={dataKey}
                name={alias}
                {...style}
                dot={dot}
            />
        );
    };

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
                    {ykeys.map((key) => drawLine(key, aliases[key], strokeStyle[key]))}
                    {isZooming && <ReferenceArea {...zoomArea}/>}
                    
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
