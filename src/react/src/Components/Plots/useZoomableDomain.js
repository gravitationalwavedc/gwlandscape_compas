import { useState } from 'react';
import { getLogTickMarks, getTickMarks } from './tickHelper';

const useZoomableDomain = ({minMaxX, minMaxY, xScale, yScale}) => {
    const initialDomain = {
        x1: minMaxX[0],
        x2: minMaxX[1],
        y1: minMaxY[0],
        y2: minMaxY[1],
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

    const xTickFunction = xScale === 'log' ? getLogTickMarks : getTickMarks;
    const yTickFunction = yScale === 'log' ? getLogTickMarks : getTickMarks;

    const xTicks = xTickFunction(domain.x1, domain.x2, 8, isZoomed);
    const yTicks = yTickFunction(domain.y1, domain.y2, 5, isZoomed);

    const xDomain = isZoomed ? [domain.x1, domain.x2] : [xTicks[0], xTicks[xTicks.length - 1]];
    const yDomain = isZoomed ? [domain.y1, domain.y2] : [yTicks[0], yTicks[yTicks.length - 1]];

    return { handleZoomIn, handleZoomOut, isZoomed, xTicks, yTicks, xDomain, yDomain };
};

export default useZoomableDomain;
