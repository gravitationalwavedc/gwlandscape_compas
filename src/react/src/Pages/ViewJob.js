import React from 'react';
import { Row, Col, Container } from 'react-bootstrap';

const ViewJob = () => (
    <Container fluid>
        <Row className="mb-3">
            <Col md={2} />
            <Col md={8}>
                <h1>Job Details</h1>
            </Col>
        </Row>
    </Container>
);


export default ViewJob;
