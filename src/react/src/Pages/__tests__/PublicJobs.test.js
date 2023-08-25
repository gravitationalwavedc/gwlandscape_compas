import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { QueryRenderer, graphql } from 'react-relay';
import {render, fireEvent} from '@testing-library/react';
import PublicJobs from '../PublicJobs';

/* global environment, router */

describe('public Job Page', () => {

    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query PublicJobsTestQuery (
              $count: Int, 
              $cursor: String, 
              $search: String) @relay_test_operation {
                ...PublicJobs_data
            }
          `}
            variables={{
                count: 10,
            }}
            render={({ error, props }) => {
                if (props) {
                    return <PublicJobs data={props} match={{}} router={router}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );

    const mockReturn = {
        CompasPublicJobNode() {
            return {
                id: '1',
                user: 'Buffy',
                jobStatus: {
                    name: 'complete'
                },
                name: 'TestJob-1',
                description: 'A test job',
            };
        }
    };

    it('renders', () => {
        expect.hasAssertions();
        const { getByText } = render(<TestRenderer />);
        environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockReturn)
        );
        expect(getByText('Jobs')).toBeInTheDocument();
    });

    it('calls refetchConnection when the serach field is updated', () => {
        expect.hasAssertions();
        const { getByPlaceholderText, getByText, queryByText } = render(<TestRenderer/>);
        environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockReturn)
        );
        // When the page first loads it should match the initial mock query
        expect(getByText('Buffy')).toBeInTheDocument();

        // Simulate searching
        const searchField = getByPlaceholderText('Search by Name, Description');
        fireEvent.change(searchField, { target: { value: 'Giles' }});

        // Refetch the container
        environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, {
                PageInfo() {
                    return {
                        hasNextPage: true,
                        endCursor: 'endcursor'
                    };
                },
                CompasPublicJobNode() {
                    return {
                        id: '2',
                        user: 'Giles',
                        jobStatus: {name: 'complete'},
                        name: 'TestJob-2',
                        description: 'A load more job.',
                    };
                }
            })
        );

        // Check the table updated.
        expect(getByText('Giles')).toBeInTheDocument();
        expect(queryByText('Buffy')).not.toBeInTheDocument();
    });

});
