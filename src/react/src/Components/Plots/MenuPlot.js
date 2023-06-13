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
    const {plotMeta, plotData} = data.plotInfo;
    const groupKeys = plotMeta.groups.map((group) => ({value: group, label: group}));
    const subgroupKeys = plotMeta.subgroups.map((subgroup) => ({value: subgroup, label: subgroup}));

    const { histData, scatterData, ...restData } = plotData;

    let stride = plotMeta.strideLength;

    return <Row>
        <Col md={4}>
            <h5>Visualisation</h5>
            <SelectInput
                data-testid='group'
                title='Group'
                options={groupKeys}
                value={plotMeta.group}
                onChange={e => {
                    relay.refetch(
                        {rootGroup: e.target.value},
                    );
                }}
            />
            <SelectInput
                data-testid='x-axis'
                title='X-axis'
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
                data-testid='y-axis'
                title='Y-axis'
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
            <Form.Group>
                <Form.Label>{`Stride = ${stride}`}</Form.Label>
                <Form.Control
                    type="range"
                    value={stride}
                    min={1}
                    max={20}
                    onChange={e => stride = e.target.value}
                    onMouseUp={() => {
                        relay.refetch(
                            {
                                rootGroup: plotMeta.group,
                                subgroupX: plotMeta.subgroupX,
                                subgroupY: plotMeta.subgroupY,
                                strideLength: stride
                            },
                        );
                    }}
                />
            </Form.Group>
        </Col>
        <Col md={8}>
            <DatasetPlot
                histData={JSON.parse(histData)}
                scatterData={JSON.parse(scatterData)}
                axis={[plotMeta.subgroupX, plotMeta.subgroupY]}
                {...restData}
            />
        </Col>
    </Row>;
};

export default createRefetchContainer(MenuPlot,
    {
        data: graphql`
        fragment MenuPlot_data on CompasDatasetModelNode @argumentDefinitions(
            rootGroup: {type: "String"},
            subgroupX: {type: "String"},
            subgroupY: {type: "String"},
            strideLength: {type: "Int"}
        ){
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
        `
    },
    graphql`
    query MenuPlotRefetchQuery(
        $publicationId: ID!
        $datasetId: ID
        $rootGroup: String
        $subgroupX: String
        $subgroupY: String
        $strideLength: Int 
    ) {
        compasPublication(id: $publicationId) {
            plotInfo: datasetModels (id: $datasetId) {
                edges {
                    node {
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
    `
);