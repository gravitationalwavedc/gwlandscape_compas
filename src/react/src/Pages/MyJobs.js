import React from 'react';
import {Col, Container, Form, InputGroup, Card, Button} from 'react-bootstrap';
import {HiOutlineSearch} from 'react-icons/hi';
import {createFragmentContainer, graphql} from 'react-relay';
import Link from 'found/Link';

const MyJobs = ({data, match, router}) => {
<<<<<<< HEAD
    const jobs = data && data.compasJobs && data.compasJobs.edges.length ? data.compasJobs.edges.map(e => e.node) : null;
=======
    const jobs = data.compasJobs ? data.compasJobs.edges.map(e => e.node) : null;
>>>>>>> added MyJobs page and a route for it
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
<<<<<<< HEAD
                    <Col>
                        <Link
                            to={'/compas/job-form'}
                            exact
                            match={match}
                            router={router}
                            as={Button}
                            variant='outline-primary'
                        >New Job</Link>
                    </Col>
=======
>>>>>>> added MyJobs page and a route for it
                </Form.Row>
            </Form>
            {jobs ?
                jobs.map(job =>
                    <Card key={job.id} className="job-card">
                        <Card.Body>
<<<<<<< HEAD
                            <Card.Title data-testid='job-name'>{job.start.name}</Card.Title>
                            <Card.Subtitle>
                                <span className={'job-'+job.jobStatus.name.toLowerCase()}>{job.jobStatus.name}</span> .
                                {job.lastUpdated}
                            </Card.Subtitle>
=======
                            <Card.Title>{job.start.name}</Card.Title>
                            <Card.Subtitle>{job.jobStatus.name} . {job.user} . {job.lastUpdated}</Card.Subtitle>
>>>>>>> added MyJobs page and a route for it
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