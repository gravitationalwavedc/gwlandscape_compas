import { useState } from 'react';
import { clampTicks, getLogTickMarks, getTickMarks } from './tickHelper';

const useZoomableDomain = ({xAxis, yAxis}) => {
    const initialDomain = {
        x1: xAxis.limits[0],
        x2: xAxis.limits[1],
        y1: yAxis.limits[0],
        y2: yAxis.limits[1],
    };
    const [domain, setDomain] = useState(initialDomain);
    const [isZoomed, setIsZoomed] = useState(false);

    const handleZoomIn = (zoomedDomain) => {
        setDomain(zoomedDomain);
        setIsZoomed(true);
    };

    const handleZoomOut = () => {
        setDomain(initialDomain);
        setIsZoomed(false);
    };

    const xDomain = [domain.x1, domain.x2];
    const yDomain = [domain.y1, domain.y2];

    let xTicks = xAxis.ticks;
    let yTicks = yAxis.ticks;

    if (isZoomed) {
        const xTickFunction = xAxis.scale === 'log' ? getLogTickMarks : getTickMarks;
        const yTickFunction = yAxis.scale === 'log' ? getLogTickMarks : getTickMarks;
    
        xTicks = xTickFunction(domain.x1, domain.x2, xTicks.length, isZoomed);
        yTicks = yTickFunction(domain.y1, domain.y2, yTicks.length, isZoomed);
    }

    xTicks = clampTicks(xDomain[0], xDomain[1], xTicks);
    yTicks = clampTicks(yDomain[0], yDomain[1], yTicks);

    return { handleZoomIn, handleZoomOut, isZoomed, xTicks, yTicks, xDomain, yDomain };
};

export default useZoomableDomain;
