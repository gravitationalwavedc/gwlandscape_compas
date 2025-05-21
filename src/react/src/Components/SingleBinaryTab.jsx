import React from 'react';
import { Col, Row, Tab } from 'react-bootstrap';

const SingleBinaryTab = ({ title, children, eventKey }) => (
    <Tab.Pane eventKey={eventKey}>
        <Row>
            <Col>
                <h3>{title}</h3>
            </Col>
        </Row>
        <Row>
            <Col>{children}</Col>
        </Row>
    </Tab.Pane>
);

export default SingleBinaryTab;
