import React from 'react';
import { Container, Col, Row, Alert} from 'react-bootstrap';
import FormCard from '../Forms/FormCard';


const JobOutput = (props) => {
    const detailedoutput = props.detailedOutputFileName;
    const error = props.error;
    const isLoading = props.isLoading;

    return (
        <Container fluid>
            {error && <Alert data-testid='error-msg'  variant="danger">{error}</Alert> }
            <React.Fragment>
                <FormCard title="Export COMPAS Output">
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