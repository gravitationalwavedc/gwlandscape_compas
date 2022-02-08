import React from 'react';
import { Container, Col, Row} from 'react-bootstrap';
import FormCard from '../Forms/FormCard';


const JobOutput = (props) => {
    const filename = props.gridfileName;
    const detailedplot = props.detailedplotfilename;
    const vanplot = props.vanplotfilename;
    const rundetails = props.rundetails;

    return (
        <Container fluid>
            <FormCard title="Evolution History">
                <Row>
                    <Col>
                        {vanplot &&
                            <img src={vanplot} alt="No image available"/>
                        }
                    </Col>
                </Row>
            </FormCard>
            <FormCard title="Detailed Evolution Plots">
                <Row>
                    <Col >
                        {detailedplot &&
                            <img src={detailedplot} alt="No image available" width='600px' height='1000px'/>
                        }
                    </Col>
                </Row>
            </FormCard>
            <FormCard title="Run Details">
                <Row>
                    <Col>
                        {rundetails &&
                            <a href={rundetails}>Download Run_Details</a>
                        }
                    </Col>
                </Row>
            </FormCard>
        </Container>


    );

};
export default JobOutput;