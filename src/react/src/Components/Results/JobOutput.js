import React from 'react';
import { Col, Row } from 'react-bootstrap';

const JobOutput = ({ detailedOutputFileName, isLoading }) => (
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
    </>
);

export default JobOutput;
