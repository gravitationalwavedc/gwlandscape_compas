import React from 'react';
import { Row, Col, Button, Container } from 'react-bootstrap';
import Link from 'found/Link';

const Home = ({ match, router }) => (
    <Container className="pt-5" fluid>
        <Row className="justify-content-center">
            <Col md="auto">
                <h1>Welcome to GWLandscape!</h1>
            </Col>
        </Row>
        <Row className="justify-content-center">
            <Col md="auto">
                <Link
                    as={Button}
                    variant="primary"
                    to="/publications/"
                    exact
                    match={match}
                    router={router}
                    className="mr-1"
                >
                    Publications
                </Link>
                <Link
                    as={Button}
                    variant="primary"
                    to="/single-binary-form/"
                    exact
                    match={match}
                    router={router}
                    className="mr-1"
                >
                    Simulate Binary
                </Link>
                <Link
                    as={Button}
                    variant="primary"
                    to="/job-form/"
                    exact
                    match={match}
                    router={router}
                    className="mr-1"
                >
                    Simulate Population
                </Link>
            </Col>
        </Row>
    </Container>
);

export default Home;
