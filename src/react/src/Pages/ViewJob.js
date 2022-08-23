import React, {useState} from 'react';
import { graphql, createFragmentContainer } from 'react-relay';
import { Row, Nav, Col, Button, Container, Tab, Toast } from 'react-bootstrap';
import moment from 'moment';
import Files from '../Components/Results/Files';
import Link from 'found/Link';
import LabelDropdown from '../Components/Results/LabelDropdown';
import PrivacyToggle from '../Components/Results/PrivacyToggle';

const ViewJob = (props) => {
    const [saved, setSaved] = useState(false); 
    const [showNotification, setShowNotification] = useState(false);

    const onSave = (saved, message) => {
        setSaved(saved);
        setShowNotification(true);
    };

    const { start, lastUpdated, userId } = props.data.compasJob;

    const updated = moment.utc(lastUpdated, 'YYYY-MM-DD HH:mm:ss UTC').local().format('llll');

    return (
        <Container className="pt-5" fluid>
            {showNotification && 
              <Toast 
                  style={{position: 'absolute', top: '56px', right:'50px'}} 
                  onClose={() => setShowNotification(false)} 
                  show={showNotification} 
                  delay={3000} 
                  autohide>
                  <Toast.Header>Saved</Toast.Header>
                  <Toast.Body>Updated job labels.</Toast.Body>
              </Toast>
            }
            <Row className="mb-3">
                <Col md={2} />
                <Col md={8}>
                    <h1>{start.name}</h1>
                    <p>{start.description}</p>
                    <p>Updated on {updated}</p>
                    <p>{props.data.compasJob.jobStatus.name}</p>
                    <LabelDropdown jobId={props.match.params.jobId} data={props.data} onUpdate={onSave} />
                    <Link as={Button} to={{
                        pathname: '/compas/job-form/duplicate/',
                        state: {
                            jobId: props.match.params.jobId
                        }
                    }} activeClassName="selected" exact match={props.match} router={props.router}>
                      Duplicate job
                    </Link>
                    <PrivacyToggle 
                        userId={userId} 
                        jobId={props.match.params.jobId} 
                        data={props.data.compasJob.start} 
                        onUpdate={onSave} />
                </Col>
            </Row>
            <Tab.Container id="jobResultsTabs" defaultActiveKey="parameters">
                <Row>
                    <Col md={2}>
                        <Nav className="flex-column">
                            <Nav.Item>
                                <Nav.Link eventKey="results">
                                    <h5>Results</h5>
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Col>
                    <Col md={8}>
                        <Tab.Content>
                            <Tab.Pane eventKey="results">
                                <Files {...props}/>
                            </Tab.Pane>
                        </Tab.Content>
                    </Col>
                </Row>
            </Tab.Container>
            <Files {...props} hidden style={{display:'none'}}/>
        </Container>
    );
};

export default createFragmentContainer(ViewJob,
    {
        data: graphql`
            fragment ViewJob_data on Query @argumentDefinitions(
                jobId: {type: "ID!"}
            ){
                compasJob (id: $jobId) {
                    id
                    userId
                    lastUpdated
                    start {
                        name
                        description
                        ...PrivacyToggle_data
                    }
                }
                ...LabelDropdown_data @arguments(jobId: $jobId)
            }
        `,
    },
);
