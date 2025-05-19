import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { QueryRenderer, graphql } from 'react-relay';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Publications from '../Publications';

/* global environment, router */

describe('publications Page', () => {
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
                query PublicationsTestQuery @relay_test_operation {
                    ...Publications_data
                }
            `}
            render={({ error, props }) => {
                if (props) {
                    return <Publications data={props} match={{}} router={router}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );

    const mockReturn = {
        CompasPublicationNodeConnection() {
            return {
                edges: [
                    {
                        node: {
                            id: '1',
                            author: 'Buffy',
                            title: 'TestPublication1',
                            year: 2022,
                            keywords: {
                                edges: [
                                    {
                                        node: {
                                            tag: 'keyword1'
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        node: {
                            id: '2',
                            author: 'Bill',
                            title: 'TestPublication2',
                            year: 1989,
                            keywords: {
                                edges: [
                                    {
                                        node: {
                                            tag: 'keyword2'
                                        }
                                    }
                                ]
                            }
                        }
                    },
                ]
            };
        }
    };

    it('renders', async () => {
        expect.hasAssertions();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation => 
            MockPayloadGenerator.generate(operation, mockReturn)
        ));
        expect(screen.getByText('Published Datasets')).toBeInTheDocument();
        expect(screen.getByText('TestPublication1')).toBeInTheDocument();
        expect(screen.getByText('TestPublication2')).toBeInTheDocument();
    });

    it('allows searching', async () => {
        expect.hasAssertions();
        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation => 
            MockPayloadGenerator.generate(operation, mockReturn)
        ));
        const search = screen.getByPlaceholderText(/Search/);
        await waitFor(() => user.type(search, 'buffy'));
        expect(screen.getByText('TestPublication1')).toBeInTheDocument();
        expect(screen.queryByText('TestPublication2')).not.toBeInTheDocument();
        
        // Restores list if search bar is cleared
        await waitFor(() => user.clear(search));
        expect(screen.getByText('TestPublication1')).toBeInTheDocument();
        expect(screen.getByText('TestPublication2')).toBeInTheDocument();
    });
});
