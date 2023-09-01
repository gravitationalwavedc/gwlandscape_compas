import React from 'react';
import { graphql, createRefetchContainer } from 'react-relay';
import { Formik } from 'formik';
import { Row, Col, Container, Button } from 'react-bootstrap';
import { IS_DEV } from '../Utils/misc';
import MenuPlot from '../Components/Plots/Publications/MenuPlot';
import SelectInput from '../Components/Forms/Atoms/SelectInput';

const fileDownloadUrl = IS_DEV
    ? 'http://localhost:8003/file_download/?fileId='
    : 'https://gwlandscape.org.au/compas/file_download/?fileId=';


const ViewPublication = ({ data, relay }) => {
    const { title, author, year, datasets, plotInfo } = data && data.compasPublication;
    const datasetOptions = datasets.edges.map(({ node }) => ({
        value: node.id,
        label: node.compasModel.name,
    }));

    const downloadFile = (e) => {
        e.preventDefault();

        // Generate a file download link and click it to download the file
        const link = document.createElement('a');
        link.href = fileDownloadUrl + plotInfo.edges[0].node.dataFile.downloadToken;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    

    return (
        <Container fluid>
            <Row className="mb-3">
                <Col md={2} />
                <Col md={8}>
                    {
                        data.compasPublication ? 
                            <>
                                <Row className="mb-3">
                                    <Col>
                                        <h1 className="text-primary">{title}</h1>
                                        <div className="text-primary">{`${author}${year ? `· ${year}` : ''}`}</div>
                                    </Col>
                                </Row>
                                <Row><Col><h5>Model</h5></Col></Row>
                                <Row>
                                    <Col md={4}>
                                        <Formik
                                            initialValues={{model: plotInfo.edges[0].node.id}}
                                            enableReinitialize
                                        >
                                            <SelectInput
                                                data-testid="model"
                                                name="model"
                                                options={datasetOptions}
                                                onChange={(e) => {
                                                    relay.refetch({ datasetId: e.target.value });
                                                }}
                                                validate={false}
                                            />
                                        </Formik>
                                    </Col>
                                    <Col md={4}>
                                        <Button
                                            variant='outline-primary'
                                            onClick={downloadFile}
                                        >
                                            Download model dataset
                                        </Button>
                                    </Col>
                                </Row>
                                <MenuPlot data={plotInfo.edges[0].node} />
                            </>
                            : <h5>Publication not found</h5>
                    }
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
                                dataFile {
                                    downloadToken
                                }
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
