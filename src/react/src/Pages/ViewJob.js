import React from 'react';
import {graphql, createFragmentContainer} from 'react-relay';
import { Row, Col, Container } from 'react-bootstrap';
import Files from '../Components/Results/Files';

const ViewJob = ({data, ...rest}) => (
    <>
        {data.compasJob ? <><Container fluid>
            <Row className="mb-3">
                <Col md={2} />
                <Col md={8}>
                    <h1>Job Details</h1>
                    {data.compasJob && <>
                        <div> Name: {data.compasJob.start.name}</div>
                        <div>Description: {data.compasJob.start.description}</div>
                        <div>Created: {data.compasJob.lastUpdated}</div>
                        <div>Private: {data.compasJob.start.private}</div>
                        <div>Status: {data.compasJob.jobStatus.name}</div>
                        <div>
                            <Files jobId={data.compasJob.id} {...rest}/>
                        </div>
                    </>}
                </Col>
            </Row>
        </Container></> : <Container><Row><Col>Job not found</Col></Row></Container>}
    </>
);


export default createFragmentContainer(ViewJob,
    {
        data: graphql`
            fragment ViewJob_data on Query @argumentDefinitions(
                jobId: {type: "ID!"}
            ){
                compasJob(id: $jobId){
                    id
                    userId
                    lastUpdated
                    start {
                        name
                        description
                        private
                    }
                    jobStatus {
                        name
                        number
                    }
                }
            }
        `,
    },
);
