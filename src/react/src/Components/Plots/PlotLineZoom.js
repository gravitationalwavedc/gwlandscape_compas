import React, { useState, useRef } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip, Customized } from 'recharts';

const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

const PlotLineZoom = ({
    syncId,
    data,
    xkey,
    ykeys,
    initialDomain,
    setDomain,
    strokeStyle,
    aliases,
    children,
    yunit,
}) => {
    const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
    const [isZooming, setIsZooming] = useState(false);
    const [isZoomed, setIsZoomed] = useState(false);

    const LineChartRef = useRef();

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

    const handleZoomOut = () => {
        setZoomArea(DEFAULT_ZOOM);
        setDomain(initialDomain);
        setIsZoomed(false);
    };

    const handleMouseDown = (e, x) => {
        x.preventDefault();
        const { chartX, chartY } = e || {};
        if (!chartX || !chartY) return;
        setIsZooming(true);
        let xValue = LineChartRef.current.state.xAxisMap[0].scale.invert(chartX);
        let yValue = LineChartRef.current.state.yAxisMap[0].scale.invert(chartY);
        setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
    };

    const handleMouseMove = (e) => {
        const { chartX, chartY } = e || {};
        if (isZooming) {
            let xValue = LineChartRef.current.state.xAxisMap[0].scale.invert(chartX);
            let yValue = LineChartRef.current.state.yAxisMap[0].scale.invert(chartY);
            setZoomArea((prev) => ({ ...prev, x2: xValue, y2: yValue }));
        }
    };

    const hasYDataInXRange = (xrangeData, minRange, maxRange) =>
        xrangeData.some((point) => {
            let datapoints = Object.values(point);
            return datapoints.some((p) => p >= minRange && p <= maxRange);
        });

    const handleMouseUp = () => {
        if (isZooming) {
            let { x1, y1, x2, y2 } = zoomArea;
            if (x1 > x2) [x1, x2] = [x2, x1];
            if (y1 > y2) [y1, y2] = [y2, y1];
            let hasDataInRange = hasYDataInXRange(
                data.filter((p) => p[xkey] >= x1 && p[xkey] <= x2),
                y1,
                y2
            );
            if (hasDataInRange) {
                setDomain({ x1: x1, y1: y1, x2: x2, y2: y2 });
                setIsZoomed(true);
            }
            setIsZooming(false);
            setZoomArea(DEFAULT_ZOOM);
        }
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
                    ref={LineChartRef}
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
