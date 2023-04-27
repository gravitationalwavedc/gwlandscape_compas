import React from 'react';
import {graphql, createFragmentContainer} from 'react-relay';
import { Row, Col, Container } from 'react-bootstrap';
import Files from '../Components/Results/Files';

const ViewJob = ({data, ...rest}) => (
    <>
        {data.compasJob ? <><Container>
            <Row className="mt-5">
                <Col>
                    {data.compasJob && <>
                        <h1>{data.compasJob.start.name}</h1>
                        <h6>
                            {data.compasJob.jobStatus.name} . Last Updated {data.compasJob.lastUpdated} .
                            {data.compasJob.user} . {data.compasJob.start.private}
                        </h6>
                        <h5>{data.compasJob.start.description}</h5>
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
