import React from 'react';
import {Button, Col, Row} from 'react-bootstrap';
import RadioGroup from './Atoms/RadioGroup';
import FormCard from './FormCard';


const DataForm = ({formik, handlePageChange}) =>
    <React.Fragment>
        <Row>
            <Col>
                <FormCard title="Data">
                    <Row>
                        <Col>
                            <RadioGroup 
                                title="Types of data" 
                                formik={formik} 
                                name="dataChoice" 
                                options={[
                                    {label:'Real', value: 'real'},
                                    // {label:'Simulated', value: 'simulated'}
                                ]} />
                        </Col>
                    </Row>
                </FormCard>
            </Col>
        </Row>
        <Row>
            <Col>
                <Button onClick={() => handlePageChange('dataParameters')}>Save and continue</Button>
            </Col>
        </Row>
    </React.Fragment>;


export default DataForm;
