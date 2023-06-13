import React from 'react';
import {graphql, createRefetchContainer} from 'react-relay';
import { Row, Col, Container, Form } from 'react-bootstrap';
import MenuPlot from '../Components/Plots/MenuPlot';

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


const ViewPublication = ({data, relay}) => {
    const {title, datasets, plotInfo} = data.compasPublication;
    const datasetOptions = datasets.edges.map(({node}) => ({
        value: node.id,
        label: node.compasModel.name
    }));

    return <Container fluid>
        <Row className="mb-3">
            <Col md={2} />
            <Col md={8}>
                <h1>Publication Details</h1>
                {
                    data.compasPublication && <>
                        <h2>{title}</h2>
                    </>
                }
                <Row>
                    <Col md={4}>
                        <h5>Model</h5>
                        <SelectInput
                            data-testid='model'
                            value={plotInfo.edges[0].node.id}
                            options={datasetOptions}
                            onChange={e => {
                                relay.refetch(
                                    {datasetId: e.target.value},
                                );
                            }}
                        />

                    </Col>
                </Row>
                <MenuPlot data={plotInfo.edges[0].node}/>
            </Col>
        </Row>
    </Container>;
};

export default createRefetchContainer(ViewPublication,
    {
        data: graphql`
            fragment ViewPublication_data on Query @argumentDefinitions(
                publicationId: {type: "ID!"},
                datasetId: {type: "ID"},
            ){
                compasPublication(id: $publicationId){
                    id
                    title
                    datasets: datasetModels {
                        edges {
                            node {
                                id
                                compasModel {
                                    name
                                }
                            }
                        }
                    }
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
        `,
    },
    graphql`
        query ViewPublicationRefetchQuery(
            $publicationId: ID!
            $datasetId: ID
            $rootGroup: String
            $subgroupX: String
            $subgroupY: String
            $strideLength: Int 
        ){
            ...ViewPublication_data @arguments(
                publicationId: $publicationId
                datasetId: $datasetId
            )
        }
    `
);
