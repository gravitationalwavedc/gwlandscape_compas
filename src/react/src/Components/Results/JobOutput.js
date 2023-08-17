import React from 'react';
import { Col, Row, Alert } from 'react-bootstrap';

const JobOutput = ({ detailedOutputFileName, error, isLoading }) => (
    <>
        <Row className="mt-2">
            <Col>
                {detailedOutputFileName ? (
                    <a data-testid="download-link" href={detailedOutputFileName}>
                        Download Output File
                    </a>
                ) : (
                    isLoading && <div>Loading...</div>
                )}
            </Col>
        </Row>
        <Row>
            <Col>
                {error && (
                    <Alert data-testid="error-msg" variant="danger">
                        {error}
                    </Alert>
                )}
            </Col>
        </Row>
    </>
);

export default JobOutput;
