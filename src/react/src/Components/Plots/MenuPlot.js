import React from 'react';
import {graphql, createRefetchContainer} from 'react-relay';

import DatasetPlot from './DatasetPlot';
import { Col, Row, Form } from 'react-bootstrap';

const SelectInput = ({ title, value, options, ...rest }) =>
    <Form.Group>
        <Form.Label>{ title }</Form.Label>
        <Form.Control
            as="select"
            custom
            value={value}
            {...rest}
        >
            {options.map(({label, value}) =>
                <option
                    value={value}
                    id={label}
                    key={label}>
                    {label}
                </option>
            )}
        </Form.Control>
    </Form.Group>;


const MenuPlot = ({data, relay}) => {
    const { datasetModels } = data;
    const plotMeta = datasetModels.edges && datasetModels.edges[0].node.plotInfo.plotMeta;
    const plotData = datasetModels.edges && datasetModels.edges[0].node.plotInfo.plotData;
    const groupKeys = plotMeta.groups.map((group) => ({value: group, label: group}));
    const subgroupKeys = plotMeta.subgroups.map((subgroup) => ({value: subgroup, label: subgroup}));

    const { histData, scatterData, ...restData } = plotData;

    return <Row>
        <Col md={8}>
            <DatasetPlot
                histData={JSON.parse(histData)}
                scatterData={JSON.parse(scatterData)}
                axis={[plotMeta.subgroupX, plotMeta.subgroupY]}
                {...restData}
            />
        </Col>
        <Col md={4}>
            <SelectInput
                data-testid='root-group'
                title='Root group'
                options={groupKeys}
                value={plotMeta.group}
                onChange={e => {
                    relay.refetch(
                        {rootGroup: e.target.value},
                    );
                }}
            />
            <SelectInput
                data-testid='subgroup-x'
                title='X subgroup'
                options={subgroupKeys}
                value={plotMeta.subgroupX}
                onChange={e => {
                    relay.refetch(
                        {
                            rootGroup: plotMeta.group,
                            subgroupY: plotMeta.subgroupY,
                            subgroupX: e.target.value
                        },
                    );
                }}
            />
            <SelectInput
                data-testid='subgroup-y'
                title='Y subgroup'
                options={subgroupKeys}
                value={plotMeta.subgroupY}
                onChange={e => {
                    relay.refetch(
                        {
                            rootGroup: plotMeta.group,
                            subgroupX: plotMeta.subgroupX,
                            subgroupY: e.target.value
                        },
                    );
                }}
            />
        </Col>
    </Row>;
};

export default createRefetchContainer(MenuPlot,
    {
        data: graphql`
        fragment MenuPlot_data on CompasPublicationNode @argumentDefinitions(
            rootGroup: {type: "String"},
            subgroupX: {type: "String"},
            subgroupY: {type: "String"},
            strideLength: {type: "Int"}
        ){
            datasetModels {
                edges {
                    node {
                        id
                        plotInfo(
                            rootGroup: $rootGroup,
                            subgroupX: $subgroupX,
                            subgroupY: $subgroupY,
                            strideLength: $strideLength
                        ){
                            plotData {
                                histData
                                sides
                                scatterData
                                minMaxX
                                minMaxY
                                logCheckX
                                logCheckY
                            }
                            plotMeta {
                                groups
                                group
                                subgroups
                                subgroupX
                                subgroupY
                                strideLength
                            }
                        }
                    }
                }
            }
        }
        `
    },
    graphql`
    query MenuPlotRefetchQuery(
        $publicationId: ID!,
        $rootGroup: String
        $subgroupX: String
        $subgroupY: String
        $strideLength: Int 
    ) {
        compasPublication(id: $publicationId) {
            ...MenuPlot_data @arguments(
                rootGroup: $rootGroup,
                subgroupX: $subgroupX,
                subgroupY: $subgroupY,
                strideLength: $strideLength
            )
        }
    }
    `
);