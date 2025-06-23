import { memo } from 'react';
import { Col, Image, Row, Table } from 'react-bootstrap';

export default memo(function VanDenHeuvel({ data }) {
    const { events } = data;
    return (
        <Col>
            {events.map((event, index) => {
                const showPrev = index !== 0 && index !== data.length - 1;
                return (
                    <Row key={event.eventChar} className="mb-4 mt-4">
                        <Col sm={1} md={1} className="text-right">
                            {event.eventChar}
                        </Col>
                        <Col>
                            <Image
                                fluid
                                src={`${import.meta.env.VITE_FRONTEND_URL}/compas/static/assets/${event.imageNum}.png`}
                                style={event.flipImage ? { transform: 'scaleX(-1)' } : {}}
                            />
                        </Col>
                        <Col>
                            <Table borderless responsive size="sm">
                                <tbody>
                                    <tr>
                                        <th width="25%">Time</th>
                                        <td>{event.time.toFixed(2)} Myr</td>
                                    </tr>
                                    <tr>
                                        <th width="25%">a</th>
                                        <td>
                                            {showPrev && event.a[0].toFixed(2) + ' to '}
                                            {event.a[1].toFixed(2)} R<sub>⊙</sub>
                                        </td>
                                    </tr>
                                    <tr>
                                        <th width="25%">
                                            M<sub>1</sub>
                                        </th>
                                        <td>
                                            {showPrev && event.m1[0].toFixed(2) + ' to '}
                                            {event.m1[1].toFixed(2)} M<sub>⊙</sub>
                                        </td>
                                    </tr>
                                    <tr>
                                        <th width="25%">
                                            M<sub>2</sub>
                                        </th>
                                        <td>
                                            {showPrev && event.m2[0].toFixed(2) + ' to '}
                                            {event.m2[1].toFixed(2)} M<sub>⊙</sub>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colSpan={2}>
                                            <h6>{event.eventString}</h6>
                                        </td>
                                    </tr>
                                </tbody>
                            </Table>
                        </Col>
                    </Row>
                );
            })}
        </Col>
    );
});
