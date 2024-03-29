import React, { useState, useRef, useCallback } from 'react';
import { ResponsiveContainer, LineChart, Line, ReferenceArea, Tooltip } from 'recharts';

const getTwoPoints = (array) => {
    const point1 = { y: array[0].y, value: array[0].value };

    const p = array.find((point) =>
        point1.value === 0 ? point.value !== point1.value : Math.abs((point.value - point1.value) / point1.value) > 1.1
    );
    const point2 = p ? { y: p.y, value: p.value } : null;
    return point2 ? [point1, point2] : null;
};

const getYconstsLinear = (point1, point2) => {
    let a = (point1.value - point2.value) / (point1.y - point2.y);
    let b = point1.value - a * point1.y;
    return [a, b];
};

const getYconstsLog = (point1, point2) => {
    let a = (point1.y - point2.y) / Math.log10(point1.value / point2.value);
    let b = point1.y - a * Math.log10(point1.value);
    return [a, b];
};

const translateChartYtoCoordY = (chartY, yconst, scaleType) => {
    if (yconst && scaleType === 'Linear') {
        return yconst[0] * chartY + yconst[1];
    }
    if (yconst && scaleType === 'Log') {
        return 10 ** ((chartY - yconst[1]) / yconst[0]);
    }
};

const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

const PlotLineZoom = ({
    syncId,
    data,
    xkey,
    ykeys,
    initialState,
    adjustDomain,
    strokeStyle,
    aliases,
    scaleType,
    children,
    yunit,
}) => {
    const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
    const [isZooming, setIsZooming] = useState(false);
    const [isZoomed, setIsZoomed] = useState(false);
    const [yconst, setYconst] = useState(null);

    const Linechartload = useCallback(
        (line) => {
            if (line && Line1) {
                const points = Line1.current.props.points;
                const twopoints = getTwoPoints(points);
                if (twopoints !== null) {
                    if (scaleType === 'Linear') setYconst(getYconstsLinear(...twopoints));
                    if (scaleType === 'Log') setYconst(getYconstsLog(...twopoints));
                }
            }
        },
        [isZoomed]
    );

    const Line1 = useRef();
    const ToolTip = useRef();

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
                ref={Line1 ? Line1 : null} //There should be new logic to get two datapoints from the plot
            />
        );
    };

    const handleZoomOUt = () => {
        setZoomArea(DEFAULT_ZOOM);
        adjustDomain(initialState); //implement this
        setIsZoomed(false);
    };

    const handleMouseDown = (e) => {
        if (!e?.activeLabel) return;
        const { activeLabel, chartY } = e || {};
        if (!activeLabel || !chartY) return;
        setIsZooming(true);
        let xValue = activeLabel;
        let yValue = translateChartYtoCoordY(chartY, yconst, scaleType);
        setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
    };

    const handleMouseMove = (e) => {
        const { activeLabel, chartY } = e || {};
        if (isZooming) {
            let xValue = activeLabel;
            let yValue = translateChartYtoCoordY(chartY, yconst, scaleType);
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
            let hasDatainRange = hasYDataInXRange(
                data.filter((p) => p[xkey] >= x1 && p[xkey] <= x2),
                y1,
                y2
            );
            if (hasDatainRange) {
                adjustDomain({ x1: x1, y1: y1, x2: x2, y2: y2 });
                setIsZoomed(true);
            }
            setIsZooming(false);
            setZoomArea(DEFAULT_ZOOM);
        }
    };

    return (
        <div style={{ width: '100%', height: '600px' }}>
            {isZoomed && <button onClick={handleZoomOUt}>Zoom Out</button>}
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
                    ref={Linechartload}
                >
                    {children}
                    {ykeys.map((key) => drawLine(key, aliases[key], strokeStyle[key]))}
                    <ReferenceArea x1={zoomArea?.x1} x2={zoomArea?.x2} y1={zoomArea?.y1} y2={zoomArea?.y2} />
                    <Tooltip
                        allowEscapeViewBox={{ x: true, y: false }}
                        offset={20}
                        ref={ToolTip}
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
