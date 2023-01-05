import React from 'react';
import { hrattr, mapScatterData } from './DataUtil';
import RenderHRDiagram from './RenderHRDiagram';

const RenderHRDiagramContainer = ({data, syncId}) => {
    const aliases = {
        teff_1: 'Temperature',
        teff_2: 'Temperature',
        luminosity_1: 'Luminosity',
        luminosity_2: 'Luminosity',
    };

    const [data1, data2] = mapScatterData(hrattr(data), aliases);

    return (
        <RenderHRDiagram data1={data1} data2={data2} syncId={syncId} />
    );
};

export default RenderHRDiagramContainer;
