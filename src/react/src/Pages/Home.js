import React from 'react';
import { Row, Col, Button, Container } from 'react-bootstrap';
import Link from 'found/Link';

const Home = ({match, router}) => <Container className="pt-5" fluid>
    <Row className='justify-content-center'>
        <Col md="auto">
            <h1>
                Welcome to GWLandscape!
            </h1>
        </Col>
    </Row>
    <Row className='justify-content-center'>
        <Col md='auto'>
            <Link 
                as={Button}
                variant="primary"
                to='/compas/publications/' 
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
                to='/compas/job-form/' 
                exact 
                match={match} 
                router={router} 
                className="mr-1"
            >
                Simulate Binary
            </Link>
        </Col>
    </Row>
</Container>;

export default Home;