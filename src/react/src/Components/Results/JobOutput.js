import React from 'react';
import { Container, Col, Row, Alert} from 'react-bootstrap';
import FormCard from '../Forms/FormCard';


const JobOutput = (props) => {
    // const filename = props.gridfileName;
    const detailedplot = props.detailedplotfilename;
    const vanplot = props.vanplotfilename;
    const detailedoutput = props.detailedOutputFileName;
    const error = props.error;
    const isLoading = props.isLoading;

    return (
        <Container fluid>
            {error && <Alert variant="danger">{error}</Alert> }
            <React.Fragment>
                <FormCard title="Evolution History">
                    <Row>
                        <Col>
                            {vanplot
                                ? <img src={vanplot} />
                                : (isLoading && <div>Loading...</div>)
                            }
                        </Col>
                    </Row>
                </FormCard>
                <FormCard title="Detailed Evolution Plots">
                    <Row>
                        <Col >
                            {detailedplot
                                ? <img src={detailedplot}  width='700px' height='1200px'/>
                                : (isLoading && <div>Loading...</div>)
                            }
                        </Col>
                    </Row>
                </FormCard>
                <FormCard title="Run COMPAS yourself">
                    <Row>
                        <Col>
                            {detailedoutput
                                ? <a data-testid="download-link" href={detailedoutput}>Download Output File</a>
                                : (isLoading && <div>Loading...</div>)
                            }
                        </Col>
                    </Row>
                </FormCard>
            </React.Fragment>
        </Container>
    );
};
export default JobOutput;