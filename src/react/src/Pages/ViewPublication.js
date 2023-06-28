import React from 'react';
import { graphql, createRefetchContainer } from 'react-relay';
import { Row, Col, Container } from 'react-bootstrap';
import MenuPlot from '../Components/Plots/Publications/MenuPlot';
import { SelectInput } from '../Components/Plots/Publications/Controls';

const ViewPublication = ({ data, relay }) => {
    const { title, author, year, datasets, plotInfo } = data && data.compasPublication;
    const datasetOptions = datasets.edges.map(({ node }) => ({
        value: node.id,
        label: node.compasModel.name,
    }));

    return (
        <Container fluid>
            <Row className="mb-3">
                <Col md={2} />
                <Col md={8}>
                    {data.compasPublication ? (
                        <>
                            <Row className="mb-3">
                                <Col>
                                    <h1 className="text-primary">{title}</h1>
                                    <div className="text-primary">{`${author}${year ? `· ${year}` : ''}`}</div>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={4}>
                                    <h5>Model</h5>
                                    <SelectInput
                                        data-testid="model"
                                        value={plotInfo.edges[0].node.id}
                                        options={datasetOptions}
                                        onChange={(e) => {
                                            relay.refetch({ datasetId: e.target.value });
                                        }}
                                    />
                                </Col>
                            </Row>
                            <MenuPlot data={plotInfo.edges[0].node} />
                        </>
                    ) : (
                        <h5>Publication not found</h5>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

export default createRefetchContainer(
    ViewPublication,
    {
        data: graphql`
            fragment ViewPublication_data on Query
            @argumentDefinitions(publicationId: { type: "ID!" }, datasetId: { type: "ID" }) {
                compasPublication(id: $publicationId) {
                    id
                    title
                    author
                    year
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
                    plotInfo: datasetModels(first: 1, id: $datasetId) {
                        edges {
                            node {
                                id
                                ...MenuPlot_data
                                    @arguments(
                                        rootGroup: $rootGroup
                                        subgroupX: $subgroupX
                                        subgroupY: $subgroupY
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
        ) {
            ...ViewPublication_data @arguments(publicationId: $publicationId, datasetId: $datasetId)
        }
    `
);
