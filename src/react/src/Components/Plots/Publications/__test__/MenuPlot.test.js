import React from 'react';
import MenuPlot from '../MenuPlot';
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
    subgroupY: 'test_subgroup_y'
};

describe('interactive plot for publications', () => {
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
                query MenuPlotTestQuery(
                    $publicationId: ID!,
                    $datasetId: ID,
                    $rootGroup: String
                    $subgroupX: String
                    $subgroupY: String
                    $strideLength: Int
                ) @relay_test_operation {
                    compasPublication(id: $publicationId) {
                        plotInfo: datasetModels (first: 1, id: $datasetId) {
                            edges {
                                node {
                                    id
                                    ...MenuPlot_data @arguments(
                                        rootGroup: $rootGroup,
                                        subgroupX: $subgroupX,
                                        subgroupY: $subgroupY,
                                        strideLength: $strideLength
                                    )
                                }
                            }
                        }
                    }
                }
            `}
            variables={{
                publicationId: 'test',
                rootGroup: 'test',
                subgroupX: 'test',
                subgroupY: 'test',
                strideLength: 1
            }}
            render={({error, props}) => {
                if (props) {
                    return <MenuPlot data={props.compasPublication.plotInfo.edges[0].node} />;
                } else if (error) {
                    return error.message;
                }
            }}
        />
    );

    const mockMenuPlotReturn = {
        PlotInfoType(){
            return {
                plotData: plotData,
                plotMeta: plotMeta
            };
        }
    };

    it('should render', async () => {
        expect.hasAssertions();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockMenuPlotReturn)
        ));
        expect(screen.getByText('Group')).toBeInTheDocument();
    });

    it('should refetch on select new root group', async () => {
        expect.hasAssertions();
        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockMenuPlotReturn)
        ));
        user.selectOptions(screen.getByTestId('group'), 'another_test_group');
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, {
                PlotInfoType(){
                    return {
                        plotData: plotData,
                        plotMeta: {
                            ...plotMeta,
                            group: 'another_test_group'
                        }
                    };
                }
            })
        ));
        // The value of the select only changes based on the props of the MenuPlot component, so this works as a test
        expect(screen.getByDisplayValue('another_test_group')).toBeInTheDocument();
    });

    it('should refetch on select new x subgroup', async () => {
        expect.hasAssertions();
        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockMenuPlotReturn)
        ));
        user.selectOptions(screen.getByTestId('x-axis'), 'test_subgroup_z');
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, {
                PlotInfoType(){
                    return {
                        plotData: plotData,
                        plotMeta: {
                            ...plotMeta,
                            subgroupX: 'test_subgroup_z'
                        }
                    };
                }
            })
        ));
        // The value of the select only changes based on the props of the MenuPlot component, so this works as a test
        expect(screen.getByDisplayValue('test_subgroup_z')).toBeInTheDocument();
    });

    it('should refetch on select new y subgroup', async () => {
        expect.hasAssertions();
        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, mockMenuPlotReturn)
        ));
        user.selectOptions(screen.getByTestId('y-axis'), 'test_subgroup_z');
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation, {
                PlotInfoType(){
                    return {
                        plotData: plotData,
                        plotMeta: {
                            ...plotMeta,
                            subgroupX: 'test_subgroup_z'
                        }
                    };
                }
            })
        ));
        // The value of the select only changes based on the props of the MenuPlot component, so this works as a test
        expect(screen.getByDisplayValue('test_subgroup_z')).toBeInTheDocument();
    });
});
