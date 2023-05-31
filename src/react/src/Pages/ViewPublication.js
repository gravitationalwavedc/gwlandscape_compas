import React from 'react';
import {graphql, createFragmentContainer} from 'react-relay';
import { Row, Col, Container } from 'react-bootstrap';
import MenuPlot from '../Components/Plots/MenuPlot';


const ViewPublication = ({data}) => {
    const {title} = data.compasPublication;

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
                {/* Page is under construction! */}
                <MenuPlot data={data.compasPublication}/>
            </Col>
        </Row>
    </Container>;
};

export default createFragmentContainer(ViewPublication,
    {
        data: graphql`
            fragment ViewPublication_data on Query @argumentDefinitions(
                publicationId: {type: "ID!"},
            ){
                compasPublication(id: $publicationId){
                    id
                    title
                    ...MenuPlot_data @arguments(
                        rootGroup: $rootGroup,
                        subgroupX: $subgroupX,
                        subgroupY: $subgroupY,
                        strideLength: $strideLength
                    )
                }
            }
        `,
    },
);
