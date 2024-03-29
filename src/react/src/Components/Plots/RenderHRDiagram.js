import React, { useState } from 'react';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Label,
    ReferenceLine,
    ScatterChart,
    Scatter,
    ZAxis,
    ReferenceArea,
} from 'recharts';
import { filterData, getReferenceLineSegment, getReferenceRangeType } from './Utils';
import { units } from './DataUtil';
import { getLogTickMarks } from './tickHelper';
import ExponentTick from './ExponentTick';

const RenderHRDiagram = ({ divStyle, syncId, data1, data2, yDomain, xDomain }) => {
    const [filteredData1, setFilteredData1] = useState([...data1]);
    const [filteredData2, setFilteredData2] = useState([...data2]);

    const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

    const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
    const [isZooming, setIsZooming] = useState(false);

    const radii = [1e-9, 1e-6, 0.001, 1, 10, 100, 1000];

    const initialState = {
        left: xDomain[0],
        right: xDomain[1],
        refAreaLeft: '',
        refAreaRight: '',
        bottom: yDomain[0],
        top: yDomain[1],
        animation: false,
    };

    const [left, setLeft] = useState(initialState.left);
    const [right, setRight] = useState(initialState.right);
    const [top, setTop] = useState(initialState.top);
    const [bottom, setBottom] = useState(initialState.bottom);

    const isZoomed = filteredData1?.length !== data1?.length || filteredData2?.length !== data2?.length;

    const drawReferenceLine = (R, xDomain, yDomain) => (
        <ReferenceLine
            key={`${R}-${xDomain}-${yDomain}`}
            label={`${R} R_sun`}
            stroke="gray"
            strokeDasharray="3 3"
            position="start"
            segment={getReferenceLineSegment(R, xDomain, yDomain)}
        />
    );

    const handleZoomOUt = () => {
        setFilteredData1([...data1]);
        setFilteredData2([...data2]);
        setZoomArea(DEFAULT_ZOOM);
        setLeft(initialState.left);
        setRight(initialState.right);
        setTop(initialState.top);
        setBottom(initialState.bottom);
    };

    const handleMouseDown = (e) => {
        const { xValue, yValue } = e || {};
        if (!xValue || !yValue) return;
        setIsZooming(true);
        setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
    };

    const handleMouseMove = (e) => {
        if (isZooming) {
            setZoomArea((prev) => ({ ...prev, x2: e?.xValue, y2: e?.yValue }));
        }
    };

    const handleMouseUp = () => {
        if (isZooming) {
            let { x1, y1, x2, y2 } = zoomArea;

            setIsZooming(false);
            setZoomArea(DEFAULT_ZOOM);

            // ensure x1 <= x2 and y1 <= y2
            if (x1 > x2) [x1, x2] = [x2, x1];
            if (y1 > y2) [y1, y2] = [y2, y1];

            const dataPointsInRange1 = filterData(filteredData1, 'Temperature', 'Luminosity', x1, x2, y1, y2);
            const dataPointsInRange2 = filterData(filteredData2, 'Temperature', 'Luminosity', x1, x2, y1, y2);

            if (dataPointsInRange1.length > 0 || dataPointsInRange2.length > 0) {
                setLeft(x1);
                setRight(x2);
                setTop(y2);
                setBottom(y1);
                setFilteredData1(dataPointsInRange1);
                setFilteredData2(dataPointsInRange2);
            }
        }
    };

    const xTicks = getLogTickMarks(left, right, 8);
    const yTicks = getLogTickMarks(bottom, top, 5);

    return (
        <div
            style={
                divStyle || {
                    width: '100%',
                    height: '600px',
                }
            }
        >
            {isZoomed && <button onClick={handleZoomOUt}>Zoom Out</button>}

            <ResponsiveContainer width="80%" height="100%">
                <ScatterChart
                    width={700}
                    height={300}
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
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        allowDataOverflow
                        dataKey="Temperature"
                        name="Temperature"
                        type="number"
                        scale="log"
                        reversed={true} //uncomment later
                        interval={0}
                        domain={[xTicks[0], xTicks[xTicks.length - 1]]}
                        ticks={xTicks}
                        tick={<ExponentTick />}
                    >
                        <Label value="Temperature(K)" position="bottom" offset={0} />
                    </XAxis>
                    <YAxis
                        allowDataOverflow
                        dataKey="Luminosity"
                        name="Luminosity"
                        type="number"
                        scale="log"
                        interval={0}
                        tick={<ExponentTick />}
                        ticks={yTicks}
                        domain={[yTicks[0], yTicks[yTicks.length - 1]]}
                        label={{
                            value: 'Luminosity/L\u{2299}',
                            angle: -90,
                            position: 'insideLeft',
                            textAnchor: 'middle',
                            offset: -7,
                        }}
                    />
                    <ZAxis dataKey="time" name="time" type="number" />
                    <Tooltip
                        allowEscapeViewBox={{ x: true, y: false }}
                        offset={20}
                        cursor={{ strokeDasharray: '3 3' }}
                        formatter={(value, name) => (
                            <>
                                {value.toFixed(2)} {units[name]}
                            </>
                        )}
                        labelFormatter={(label) => `${label.toFixed(2)}`}
                    />
                    <Legend
                        wrapperStyle={{ paddingLeft: '40px' }}
                        layout="vertical"
                        align="right"
                        verticalAlign="top"
                    />
                    {radii
                        .filter((r) => getReferenceRangeType(r, xDomain, yDomain))
                        .map((r) => drawReferenceLine(r, xDomain, yDomain))}
                    <Scatter name="Star1" data={filteredData1} line={{ strokeWidth: 2 }} fill="red" radius={2} />
                    <Scatter name="Star2" data={filteredData2} line={{ strokeWidth: 2 }} fill="blue" />
                    <ReferenceArea x1={zoomArea?.x1} x2={zoomArea?.x2} y1={zoomArea?.y1} y2={zoomArea?.y2} />
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RenderHRDiagram;
