import React, { memo } from 'react';
import { Col, Image, Row } from 'react-bootstrap';
import { vdhattr } from './DataUtil';
import { eventAlphabet, getEvents } from './VanDenHeuvelUtils';

const DOMAIN = process.env.NODE_ENV !== 'development' ? '' : 'http://localhost:3004';

export default memo(function VanDenHeuvel({ data }) {
    const vdhattrData = vdhattr(data);
    const [imageIndices, sequenceIndices, eventStrings] = getEvents(vdhattrData);

    return (
        <Col>
            {sequenceIndices && sequenceIndices.map((index, i) =>
                imageIndices[i] ? <Row md={3} sm={3} key={i} className="mb-4">
                    <Col sm={1} md={1} className="text-right">{eventAlphabet[i]}</Col>
                    <Col>
                        <Image fluid src={`${DOMAIN}/compas/static/assets/${imageIndices[i]}.png`} />
                    </Col>
                    <Col>
                        Time = {vdhattrData.time[index].toFixed(2)} Myr, 
                        a = {vdhattrData.semimajor[index].toFixed(2)} R<sub>⊙</sub>
                        M<sub>1</sub> = {vdhattrData.mass1[index].toFixed(2)} M<sub>⊙</sub>, 
                        M<sub>2</sub> = {vdhattrData.mass2[index].toFixed(2)} M<sub>⊙</sub>, 
                        {eventStrings[i]}
                    </Col>
                </Row> : null)
            }
        </Col >
    );
});