import React from 'react';
import {Col, Container, Form, InputGroup, Card, Button} from 'react-bootstrap';
import {HiOutlineSearch} from 'react-icons/hi';
import InfiniteScroll from 'react-infinite-scroll-component';
import {createPaginationContainer, graphql} from 'react-relay';
import Link from 'found/Link';


const RECORDS_PER_PAGE = 10;

const MyJobs = ({data, match, router, relay}) => {
    const jobs = data && data.compasJobs && data.compasJobs.edges.length > 0 ?
        data.compasJobs.edges.map(e => e.node) : null;

    const _loadMore = () => {
        if (! relay.hasMore() || relay.isLoading()) {
            return;
        }
        relay.loadMore(
            RECORDS_PER_PAGE,
            error => {
                console.log(error);
            },
        );
    };

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
                </Form.Row>
            </Form>
            {jobs ?
                <InfiniteScroll
                    next={_loadMore}
                    hasMore={relay.hasMore}
                    loader='Scroll to load more...'
                    dataLength={jobs.length}>{
                        jobs.map(job =>
                            <Card key={job.id} className="job-card">
                                <Card.Body>
                                    <Card.Title data-testid='job-name'>{job.start.name}</Card.Title>
                                    <Card.Subtitle>
                                        <span className={'job-'+job.jobStatus.name.toLowerCase()}>
                                            {job.jobStatus.name}
                                        </span> . {job.lastUpdated}
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
                            </Card>)}
                </InfiniteScroll>
                : <p data-testid='no-jobs'>No Jobs Found!</p>
            }
        </Container>
    );
};

// export default createFragmentContainer(MyJobs, {
//     data: graphql`
//         fragment MyJobs_data on Query {
//             compasJobs {
//                 edges {
//                     node {
//                         id
//                         user
//                         userId
//                         lastUpdated
//                         start {
//                           name
//                           description
//                           private
//                         }
//                         jobStatus{
//                           name
//                           date
//                         }
//                     }
//                 }
//             }
//         }
//     `
// })


export default createPaginationContainer(MyJobs,
    {
        data: graphql`
            fragment MyJobs_data on Query {
                compasJobs(
                    first: $count,
                    after: $cursor,
                ) @connection(key: "MyJobs_compasJobs") {
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
        `,
    },
    {
        direction: 'forward',
        query: graphql`
            query MyJobsForwardQuery(
                $count: Int!,
                $cursor: String,
            ) {
              ...MyJobs_data
            }
        `,
        getConnectionFromProps(props) {
            return props.data && props.data.compasJobs;
        },

        getFragmentVariables(previousVariables, totalCount) {
            return {
                ...previousVariables,
                count: totalCount
            };
        },

        getVariables(props, {count, cursor}, {orderBy}) {
            return {
                count,
                cursor,
                orderBy,
            };
        }
    }
);
;