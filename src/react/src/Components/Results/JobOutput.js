import React from 'react';
import { Col, Row, Alert } from 'react-bootstrap';

const JobOutput = ({ detailedOutputFileName, error, isLoading }) => (
    <>
        <Row>
            <Col>
                <h4>Compas Output</h4>
            </Col>
            <Col>
                {detailedOutputFileName
                    ? <a 
                        data-testid="download-link"
                        className='float-right mr-4'
                        href={detailedOutputFileName}>Download Output File</a>
                    : (isLoading && <div>Loading...</div>)
                }
            </Col>
        </Row>
        <Row>
            <Col>
                {error && <Alert data-testid='error-msg' variant="danger">{error}</Alert>}
            </Col>
        </Row>
    </>
);

export default JobOutput;
