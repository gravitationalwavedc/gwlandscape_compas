import React from 'react';
import {Col, Container, Form, InputGroup, Card, Button} from 'react-bootstrap';
import {HiOutlineSearch} from 'react-icons/hi';
import {createFragmentContainer, graphql} from 'react-relay';
import Link from 'found/Link';

const MyJobs = ({data, match, router}) => {
    const jobs = data.compasJobs ? data.compasJobs.edges.map(e => e.node) : null;
    return (
        <Container>
            <h1 className="pt-5 mb-4">
                My Jobs
            </h1>
            <Form>
                <Form.Row>
                    <Col lg={6}>
                        <Form.Group controlId="searchJobs">
                            <InputGroup>
                                <InputGroup.Prepend>
                                    <InputGroup.Text>
                                        <HiOutlineSearch />
                                    </InputGroup.Text>
                                </InputGroup.Prepend>
                                <Form.Control
                                    className="text-left"
                                    placeholder="Search by Name, Description or Last Updated Date"
                                />
                            </InputGroup>
                        </Form.Group>
                    </Col>
                </Form.Row>
            </Form>
            {jobs ?
                jobs.map(job =>
                    <Card key={job.id} className="job-card">
                        <Card.Body>
                            <Card.Title>{job.start.name}</Card.Title>
                            <Card.Subtitle>
                                <span className={'job-'+job.jobStatus.name.toLowerCase()}>{job.jobStatus.name}</span> .
                                {job.lastUpdated}
                            </Card.Subtitle>
                            <Card.Text>{job.start.description}</Card.Text>
                            <Link
                                to={'/compas/job-results/' + job.id + '/'}
                                exact
                                match={match}
                                router={router}
                                as={Button}
                                variant='outline-primary'
                            >Explore Job Details</Link>
                        </Card.Body>
                    </Card>)
                : <p>No Jobs Found!</p>
            }
        </Container>
    );
};

export default createFragmentContainer(MyJobs, {
    data: graphql`
        fragment MyJobs_data on Query {
            compasJobs {
                edges {
                    node {
                        id
                        user
                        userId
                        lastUpdated
                        start {
                          name
                          description
                          private
                        }
                        jobStatus{
                          name
                          date
                        }
                    }
                }
            }
        }
    `
});