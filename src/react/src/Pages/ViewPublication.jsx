import React from 'react';
import { graphql, createRefetchContainer } from 'react-relay';
import { Formik } from 'formik';
import { Row, Col, Container, Button } from 'react-bootstrap';
import MenuPlot from '../Components/Plots/Publications/MenuPlot';
import SelectInput from '../Components/Forms/Atoms/SelectInput';

const fileDownloadUrl = `${import.meta.env.VITE_BACKEND_URL}/file_download/?fileId=`;

const ViewPublication = ({ data, relay }) => {
  const { title, author, year, datasets, keywords, plotInfo } = data && data.compasPublication;
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
                <Row className="mt-3 mb-3">
                  <Col>
                    <h2 className="text-primary font-weight-bold">{title}</h2>
                    <h5 className="text-primary">{`${author}${year ? ` · ${year}` : ''}`}</h5>
                    <h6 className="font-italic">
                      {keywords?.edges.map(({ node }) => node.tag).join(', ')}
                    </h6>
                  </Col>
                </Row>
                <Row><Col><h5>Model</h5></Col></Row>
                <Row>
                  <Col md={4}>
                    <Formik
                      initialValues={{ model: plotInfo.edges[0].node.id }}
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
                    keywords {
                        edges {
                            node {
                                tag
                            }
                        }
                    }
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
