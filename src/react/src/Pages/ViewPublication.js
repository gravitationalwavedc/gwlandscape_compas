import React from 'react';
import {graphql, createFragmentContainer} from 'react-relay';
import { Row, Col, Container } from 'react-bootstrap';
import DatasetPlot from '../Components/Plots/DatasetPlot';


const ViewPublication = ({data}) => {
    const {title, datasetModels} = data.compasPublication;
    const plotData = datasetModels.edges && JSON.parse(datasetModels.edges[0].node.plotData);

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
                Page is under construction!
                {/* <DatasetPlot inpdata={plotData.truncData} axis={['x', 'y']}/> */}
            </Col>
        </Row>
    </Container>;
};

export default createFragmentContainer(ViewPublication,
    {
        data: graphql`
            fragment ViewPublication_data on Query @argumentDefinitions(
                publicationId: {type: "ID!"},
                rootGroup: {type: "String"},
                subgroupX: {type: "String"},
                subgroupY: {type: "String"},
                strideLength: {type: "Int"}
            ){
                compasPublication(id: $publicationId){
                    id
                    title
                    datasetModels {
                        edges {
                            node {
                                id
                                plotData(
                                    rootGroup: $rootGroup,
                                    subgroupX: $subgroupX,
                                    subgroupY: $subgroupY,
                                    strideLength: $strideLength
                                )
                                plotMeta(rootGroup: $rootGroup)
                            }
                        }
                    }
                }
            }
        `,
    },
);
