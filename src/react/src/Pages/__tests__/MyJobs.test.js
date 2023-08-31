import React from 'react';
import { QueryRenderer, graphql } from 'react-relay';
import {render, waitFor} from '@testing-library/react';
import MyJobs from '../MyJobs';

/* global environment, router */

describe('my Jobs Page', () => {

    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query MyJobsTestQuery (
              $count: Int, 
              $cursor: String,
              $orderBy: String
              )
              @relay_test_operation {
                ...MyJobs_data
            }
          `}
            variables={{
                count: 10,
                orderBy: '-lastUpdated'
            }}
            render={({error, props}) => {
                if (props) {
                    return <MyJobs data={props} match={{}} router={router}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );

    it('renders with data', async () => {
        expect.hasAssertions();
        const {getByTestId} = render(<TestRenderer/>);
        await waitFor(() => environment.mock.resolveMostRecentOperation( {
            data: {
                compasJobs: {
                    edges: [
                        {
                            node: {
                                id: 'Q29tcGFzSm9iTm9kZToxMjM=',
                                user: 'Eman Ali',
                                userId: 1,
                                lastUpdated: '2022-11-16 23:27:32 UTC',
                                start: {
                                    name: 'Hello_me',
                                    description: 'A good description is specific, unique, and memorable.',
                                    private: false
                                },
                                jobStatus: {
                                    name: 'Completed',
                                    date: '2022-11-16 23:30:17 UTC'
                                }
                            }
                        }
                    ]
                }
            }
        }
        ));
        expect(getByTestId('job-name')).toBeInTheDocument();
    });

    it('renders without data', async () => {
        expect.hasAssertions();
        const {getByTestId} = render(<TestRenderer/>);
        await waitFor(() => environment.mock.resolveMostRecentOperation( {
            data: {
                compasJobs: {
                    edges: []
                }
            }
        }
        ));
        expect(getByTestId('no-jobs')).toBeInTheDocument();
    });
});