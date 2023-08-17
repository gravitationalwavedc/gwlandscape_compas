import React, { memo, useMemo } from 'react';
import { hrattr, mapScatterData } from './DataUtil';
import RenderHRDiagram from './RenderHRDiagram';

const RenderHRDiagramContainer = ({ data, syncId }) => {
    const aliases = {
        teff_1: 'Temperature',
        teff_2: 'Temperature',
        luminosity_1: 'Luminosity',
        luminosity_2: 'Luminosity',
    };

    const [data1, data2, yDomain, xDomain] = useMemo(() => {
        const [raw1, raw2] = mapScatterData(hrattr(data), aliases);

        const data1 = raw1.filter((point) => point.Luminosity > 100);
        const data2 = raw2.filter((point) => point.Luminosity > 100);

        const maxY = [...data1, ...data2].reduce((acc, curr) => (curr.Luminosity > acc ? curr.Luminosity : acc), 0);
        const minY = data2[0].Luminosity;

        const maxX = Math.ceil(
            [...data1, ...data2].reduce((acc, curr) => (curr.Temperature > acc ? curr.Temperature : acc), 0)
        );
        const minX = Math.floor(
            [...data1, ...data2].reduce((acc, curr) => (curr.Temperature < acc ? curr.Temperature : acc), maxX)
        );

        return [data1, data2, [minY, maxY], [minX, maxX]];
    }, [data]);

    return <RenderHRDiagram data1={data1} data2={data2} syncId={syncId} yDomain={yDomain} xDomain={xDomain} />;
};

export default memo(RenderHRDiagramContainer);
