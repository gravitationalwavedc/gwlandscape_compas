import React from 'react';
import ViewPublication from '../ViewPublication';
import {graphql, QueryRenderer} from 'react-relay';
import {MockPayloadGenerator} from 'relay-test-utils';
import {render, waitFor, screen} from '@testing-library/react';
import 'regenerator-runtime/runtime';

/* global environment */

const histData = `[
    {
        "x": 1,
        "y": 1,
        "counts": 1
    }
]`;

const scatterData = `[
    {
        "x": 1,
        "y": 1
    }
]`;

describe('view Compas Job details page', () => {
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
                query ViewPublicationTestQuery(
                    $publicationId: ID!,
                    $rootGroup: String
                    $subgroupX: String
                    $subgroupY: String
                    $strideLength: Int
                ) @relay_test_operation {
                    ...ViewPublication_data @arguments(
                        publicationId: $publicationId,
                    )
                }
            `}
            variables={{
                jobId: 'Q29tcGFzSm9iTm9kZToxNTA='
            }}
            render={({error, props}) => {
                if(props) {
                    return <ViewPublication data={props} />;
                } else if (error) {
                    return error.message;
                }
            }}
        />
    );

    const mockViewCompasPublicationReturn = {
        CompasPublicationNode(){
            return {
                id: 'Q29tcGFzSm9iTm9kZToxNTA=',
                title: 'Test Title',
                datasetModels: {
                    edges: [
                        {
                            node: {
                                plotInfo: {
                                    plotData: {
                                        histData: histData,
                                        scatterData: scatterData
                                    },
                                }
                            }
                        }
                    ]
                }
            };
        }
    };

    it('should render the actual page', async () => {
        expect.hasAssertions();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockViewCompasPublicationReturn)
        ));
        expect(screen.getByText('Test Title')).toBeInTheDocument();
    });
});
