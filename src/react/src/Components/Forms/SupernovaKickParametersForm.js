import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';

const SupernovaKickParametersForm = ({formik}) => {
    const [show, setShow] = useState(false);
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <h2>Supernova Remnant and Kick Parameters</h2>
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Input
                        formik={formik}
                        title="Number of Systems"
                        name="numberOfSystems"
                        type="number"
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default SupernovaKickParametersForm;