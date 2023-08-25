import React, {useState, useEffect} from 'react';
import {Col, Container, Form, InputGroup, Card, Button} from 'react-bootstrap';
import {HiOutlineSearch} from 'react-icons/hi';
import InfiniteScroll from 'react-infinite-scroll-component';
import {createPaginationContainer, graphql} from 'react-relay';
import Link from 'found/Link';


const RECORDS_PER_PAGE = 10;

const PublicJobs = ({data, match, router, relay}) => {
    const jobs = data && data.publicCompasJobs && data.publicCompasJobs.edges.length > 0 ?
        data.publicCompasJobs.edges.map(e => e.node) : null;
    const [search, setSearch] = useState('');

    const _loadMore = () => {
        if (! relay.hasMore() || relay.isLoading()) {
            return;
        }
        relay.loadMore(RECORDS_PER_PAGE);
    };

    useEffect(() => handleSearchChange(), [search]);

    const handleSearchChange = () => {
        const refetchVariables = {
            count: RECORDS_PER_PAGE,
            search: search
        };
        relay.refetchConnection(1, null, refetchVariables);
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
                                    onChange={({target}) => setSearch(target.value)}
                                />
                            </InputGroup>
                        </Form.Group>
                    </Col>
                    <Col lg={2}>
                        <Link
                            to={'/compas/job-form'}
                            exact
                            match={match}
                            router={router}
                            as={Button}
                            variant='outline-primary'
                        >New Job</Link>
                    </Col>
                    <Col lg={3}>
                        <Link
                            to={'/compas/my-jobs/'}
                            exact
                            match={match}
                            router={router}
                            as={Button}
                            variant='outline-primary'
                        >My Jobs</Link>
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


export default createPaginationContainer(PublicJobs,
    {
        data: graphql`
            fragment PublicJobs_data on Query {
                publicCompasJobs(
                    first: $count,
                    after: $cursor,
                    search: $search
                ) @connection(key: "PublicJobs_publicCompasJobs") {
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    edges {
                        node {
                            id
                            user
                            name
                            description
                            jobStatus{
                              name
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
            query PublicJobsForwardQuery(
                $count: Int!,
                $cursor: String,
                $search: String
            ) {
              ...PublicJobs_data
            }
        `,
        getConnectionFromProps(props) {
            return props.data && props.data.publicCompasJobs;
        },

        getFragmentVariables(previousVariables, totalCount) {
            return {
                ...previousVariables,
                count: totalCount
            };
        },

        getVariables(props, {count, cursor}, {}) {
            return {
                count,
                cursor
            };
        }
    }
);
