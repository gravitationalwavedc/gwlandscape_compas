import React from 'react';
import ViewPublication from '../ViewPublication';
import {graphql, QueryRenderer} from 'react-relay';
import {MockPayloadGenerator} from 'relay-test-utils';
import {render, waitFor, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import 'regenerator-runtime/runtime';

/* global environment */

const plotData = {
    histData: `[
        {
            "x": 1,
            "y": 1,
            "counts": 1
        }
    ]`,
    scatterData: `[
        {
            "x": 1,
            "y": 1
        }
    ]`
};

const plotMeta = {
    groups: ['test_group', 'another_test_group'],
    group: 'test_group',
    subgroups: ['test_subgroup_x', 'test_subgroup_y', 'test_subgroup_z'],
    subgroupX: 'test_subgroup_x',
    subgroupY: 'test_subgroup_y',
    strideLength: 1
};

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

    const mockViewCompasPublicationReturn = (i) => ({
        CompasPublicationNode(){
            return {
                id: 'Q29tcGFzSm9iTm9kZToxNTA=',
                title: 'Test Title',
                datasets: {
                    edges: [
                        {node: {id: 'test-id-1', compasModel: {name: 'Test Model 1'}}},
                        {node: {id: 'test-id-2', compasModel: {name: 'Test Model 2'}}},
                    ]
                },
                plotInfo: {
                    edges: [
                        {node: {id: `test-id-${i}`, plotData, plotMeta}},
                    ]
                }
            };
        }
    });

    it('should render the actual page', async () => {
        expect.hasAssertions();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockViewCompasPublicationReturn(1))
        ));
        expect(screen.getByText('Test Title')).toBeInTheDocument();
    });

    it('should refetch on select new root group', async () => {
        expect.hasAssertions();
        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockViewCompasPublicationReturn(1))
        ));
        expect(screen.getByDisplayValue('Test Model 1')).toBeInTheDocument();
        await user.selectOptions(screen.getByTestId('model'), 'Test Model 2');
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockViewCompasPublicationReturn(2))
        ));
        // The value of the select only changes based on the props of the MenuPlot component, so this works as a test
        expect(screen.getByDisplayValue('Test Model 2')).toBeInTheDocument();
    });
});
