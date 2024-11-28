import React, { useRef, useState } from 'react';
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
import ExponentTick from './ExponentTick';
import useZoom from './useZoom';
import useZoomableDomain from './useZoomableDomain';

const RenderHRDiagram = ({ divStyle, syncId, data1, data2, minMaxY, minMaxX }) => {
    const [filteredData1, setFilteredData1] = useState([...data1]);
    const [filteredData2, setFilteredData2] = useState([...data2]);

    const xScale = 'log';
    const yScale = 'log';

    const {
        handleZoomIn, handleZoomOut, isZoomed, xTicks, yTicks, xDomain, yDomain
    } = useZoomableDomain({minMaxX, minMaxY, xScale, yScale});

    const onZoomIn = ({x1, y1, x2, y2}) => {
        const dataPointsInRange1 = filterData(filteredData1, 'Temperature', 'Luminosity', x1, x2, y1, y2);
        const dataPointsInRange2 = filterData(filteredData2, 'Temperature', 'Luminosity', x1, x2, y1, y2);
    
        if (dataPointsInRange1.length > 0 || dataPointsInRange2.length > 0) {
            handleZoomIn({x1, y1, x2, y2});
            setFilteredData1(dataPointsInRange1);
            setFilteredData2(dataPointsInRange2);
        }
    };

    const onZoomOut = () => {
        setFilteredData1([...data1]);
        setFilteredData2([...data2]);
        handleZoomOut();
    };

    const chartRef = useRef();

    const { isZooming, zoomArea, handleMouseDown, handleMouseMove, handleMouseUp } = useZoom({onZoomIn, chartRef});

    const radii = [1e-9, 1e-6, 0.001, 1, 10, 100, 1000];

    const drawReferenceLine = (R, xDomain, yDomain) => (
        <ReferenceLine
            key={`${R}-${xDomain}-${yDomain}`}
            label={`${R} R\u{2299}`}
            stroke="gray"
            strokeDasharray="3 3"
            position="start"
            segment={getReferenceLineSegment(R, xDomain, yDomain)}
        />
    );

    return (
        <div
            style={
                divStyle || {
                    width: '100%',
                    height: '600px',
                }
            }
        >
            {isZoomed && <button onClick={onZoomOut}>Zoom Out</button>}

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
                    ref={chartRef}
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
                        domain={xDomain}
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
                        domain={yDomain}
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
                    {isZooming && <ReferenceArea {...zoomArea} />}
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RenderHRDiagram;
