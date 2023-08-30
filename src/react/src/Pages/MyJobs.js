import React from 'react';
import {Col, Container, Card, Button, Row} from 'react-bootstrap';
import InfiniteScroll from 'react-infinite-scroll-component';
import {createPaginationContainer, graphql} from 'react-relay';
import Link from 'found/Link';


const RECORDS_PER_PAGE = 100;

const MyJobs = ({data, match, router, relay}) => {
    const jobs = data && data.compasJobs && data.compasJobs.edges.length > 0 ?
        data.compasJobs.edges.map(e => e.node) : null;

    const _loadMore = () => {
        if (! relay.hasMore() || relay.isLoading()) {
            return;
        }
        relay.loadMore(RECORDS_PER_PAGE);
    };


    return (
        <Container>
            <Row>
                <Col lg={6}>
                    <h1 className="pt-5 mb-3">
                        My Jobs
                    </h1>
                </Col>
                <Col lg={2} className="pt-5 mb-2">
                    <Link
                        to={'/compas/jobs/'}
                        exact
                        match={match}
                        router={router}
                        as={Button}
                        variant='outline-primary'
                    >Public Jobs</Link>
                </Col>
                <Col lg={2} className="pt-5 mb-2">
                    <Link
                        to={'/compas/job-form'}
                        exact
                        match={match}
                        router={router}
                        as={Button}
                        variant='primary'
                    >New Job</Link>
                </Col>
            </Row>

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

export default createPaginationContainer(MyJobs,
    {
        data: graphql`
            fragment MyJobs_data on Query {
                compasJobs(
                    first: $count,
                    after: $cursor,
                    orderBy: $orderBy
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
                $orderBy: String
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
                orderBy: orderBy,
            };
        }
    }
);
