import { useState } from 'react';

const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

const useZoom = ({ onZoomIn, chartRef }) => {
    const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
    const [isZooming, setIsZooming] = useState(false);
    const [isMoving, setIsMoving] = useState(false);

    const handleMouseDown = (e, x) => {
        x.preventDefault();
        const { chartX, chartY } = e || {};
        if (!chartX || !chartY) return;
        setIsZooming(true);
        let xValue = chartRef.current.state.xAxisMap[0].scale.invert(chartX);
        let yValue = chartRef.current.state.yAxisMap[0].scale.invert(chartY);
        setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
    };

    const handleMouseMove = (e) => {
        const { chartX, chartY } = e || {};
        if (isZooming) {
            setIsMoving(true);
            let xValue = chartRef.current.state.xAxisMap[0].scale.invert(chartX);
            let yValue = chartRef.current.state.yAxisMap[0].scale.invert(chartY);
            setZoomArea((prev) => ({ ...prev, x2: xValue, y2: yValue }));
        }
    };

    const handleMouseUp = () => {
        if (isZooming) {
            setIsZooming(false);

            if (isMoving) {
                let { x1, y1, x2, y2 } = zoomArea;
                if (x1 > x2) [x1, x2] = [x2, x1];
                if (y1 > y2) [y1, y2] = [y2, y1];

                setIsMoving(false);
                setZoomArea(DEFAULT_ZOOM);

                onZoomIn({ x1, y1, x2, y2 });
            }
        }
    };

    return {
        handleMouseDown,
        handleMouseMove,
        handleMouseUp,
        isZooming,
        zoomArea,
    };
};

export default useZoom;
