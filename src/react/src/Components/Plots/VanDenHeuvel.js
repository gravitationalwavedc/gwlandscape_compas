import React, { memo } from 'react';
import { Col, Image, Row, Table } from 'react-bootstrap';
import { vdhattr } from './DataUtil';
import { eventAlphabet, getEvents } from './VanDenHeuvelUtils';

const DOMAIN = process.env.NODE_ENV !== 'development' ? '' : 'http://localhost:3004';

export default memo(function VanDenHeuvel({ data }) {
    const vdhattrData = vdhattr(data);
    const [imageIndices, sequenceIndices, eventStrings] = getEvents(vdhattrData);

    return (
        <Col>
            {sequenceIndices && sequenceIndices.map((index, i) =>
                imageIndices[i] ? <Row key={i} className="mb-4 mt-4">
                    <Col sm={1} md={1} className="text-right">{eventAlphabet[i]}</Col>
                    <Col>
                        <Image fluid src={`${DOMAIN}/compas/static/assets/${imageIndices[i]}.png`} />
                    </Col>
                    <Col>
                        <Table borderless responsive size="sm">
                            <tbody>
                                <tr>
                                    <th>
                                        Time
                                    </th>
                                    <td>
                                        {vdhattrData.time[index].toFixed(2)} Myr
                                    </td>
                                </tr>
                                <tr>
                                    <th>
                                        a
                                    </th>
                                    <td>
                                        {vdhattrData.semimajor[index].toFixed(2)} R<sub>⊙</sub>
                                    </td>
                                </tr>
                                <tr>
                                    <th>
                                        M<sub>1</sub>
                                    </th>
                                    <td>
                                        {vdhattrData.mass1[index].toFixed(2)} M<sub>⊙</sub>
                                    </td>
                                </tr>
                                <tr>
                                    <th>
                                        M<sub>2</sub>
                                    </th>
                                    <td>
                                        {vdhattrData.mass2[index].toFixed(2)} M<sub>⊙</sub>
                                    </td>
                                </tr>
                                <tr>
                                    <td colSpan={2}>
                                        <h6>{eventStrings[i]}</h6>
                                    </td>
                                </tr>
                            </tbody>
                        </Table>
                    </Col>
                </Row> : null)
            }
        </Col >
    );
});