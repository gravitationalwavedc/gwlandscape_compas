import React from 'react';
import {graphql, createFragmentContainer} from 'react-relay';
import {Row, Col, Container, Nav, Tab} from 'react-bootstrap';
import Files from '../Components/Results/Files';
import Parameters from '../Components/Results/Parameters';

const ViewJob = ({data, ...rest}) => (
    <>
        {data.compasJob ? <><Container>
            {data.compasJob && <>
                <Row className="mt-5 mb-3">
                    <Col>
                        <h1>{data.compasJob.start.name}</h1>
                        <h6 data-testid="jobInfo">
                            {data.compasJob.jobStatus.name} . Last Updated {data.compasJob.lastUpdated} .
                            {data.compasJob.user} . {data.compasJob.start.private? ' Private' : ' Public'}
                        </h6>
                        <h5>{data.compasJob.start.description}</h5>
                    </Col>
                </Row>
                <Tab.Container id="job_info_tabs" defaultActiveKey="parameters">
                    <Row>
                        <Col md={3}>
                            <Nav fill variant="pills" className="flex-column text-center">
                                <Nav.Item>
                                    <Nav.Link eventKey="parameters">Parameters</Nav.Link>
                                </Nav.Item>
                                <Nav.Item>
                                    <Nav.Link eventKey="results">Results</Nav.Link>
                                </Nav.Item>
                            </Nav>
                        </Col>
                        <Col md={9}>
                            <Tab.Content className="mt-2">
                                <Tab.Pane eventKey="results">
                                    <Files jobId={data.compasJob.id} {...rest}/>
                                </Tab.Pane>
                                <Tab.Pane eventKey="parameters">
                                    <Parameters jobData={data.compasJob} {...rest}/>
                                </Tab.Pane>
                            </Tab.Content>
                        </Col>
                    </Row>
                </Tab.Container>
            </>}
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
                    user
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
                    ...Parameters_jobData
                }
            }
        `,
    },
);
