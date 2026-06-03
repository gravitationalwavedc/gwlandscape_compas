import { Col, Row } from 'react-bootstrap';

const JobOutput = ({ detailedOutputFileName, isLoading }) => (
    <>
        <Row className="mt-2">
            <Col>
                {detailedOutputFileName ? (
                    <>
                        <a className="mr-4" data-testid="download-link" href={detailedOutputFileName}>
                            Download Output File
                        </a>
                        <a data-testid="download-link" href={detailedOutputFileName}>
                            Download VIMES Movie
                        </a>
                    </>
                ) : (
                    isLoading && <div>Loading...</div>
                )}
            </Col>
        </Row>
    </>
);

export default JobOutput;
