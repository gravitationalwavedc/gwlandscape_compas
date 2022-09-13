import React from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';

const InitialParametersForm = ({formik}) => {
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <h2>Population</h2>
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

export default InitialParametersForm;
