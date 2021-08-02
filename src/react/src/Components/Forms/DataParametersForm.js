import React from 'react';
import {Button, Col, Row, Form} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';

const DataParametersForm = ({formik, handlePageChange}) => {
    const realData = formik.values.dataChoice === 'real';
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Source Parameters">
                        {realData &&
                        <Row>
                            <Col>
                                <Form.Group controlId="sourceDataset">
                                    <Form.Label>Source Dataset</Form.Label>
                                    <Form.Control
                                        name="sourceDataset"
                                        as="select"
                                        custom
                                        {...formik.getFieldProps('sourceDataset')}>
                                        {/*<option value='o1'>O1</option>*/}
                                        {/*<option value='o2'>O2</option>*/}
                                        <option value='o3'>O3</option>
                                    </Form.Control>
                                </Form.Group>
                            </Col>
                        </Row>
                        }
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Start frequency of band (Hz)"
                                    name="startFrequencyBand"
                                    type="number"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Minimum start time (GPS)"
                                    name="minStartTime"
                                    type="number"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Maximum start time (GPS)"
                                    name="maxStartTime"
                                    type="number"
                                />
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
            <Row>
                <Col>
                    <FormCard
                        title="Atom Generation Parameters">
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Orbit projected semi-major axis (a sin i, seconds)"
                                    name="asini"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Time of ascension (GPS s)"
                                    name="orbitTp"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Frequency search band"
                                    name="freqBand"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Right ascension (rad)"
                                    name="alpha"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Declination (rad)"
                                    name="delta"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Orbital period (s)"
                                    name="orbitPeriod"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Coherence time (s)"
                                    name="driftTime"
                                    type="number"/>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Frequency step size (Hz)"
                                    name="dFreq"
                                    type="number"/>
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
            <Row>
                <Col>
                    <Button onClick={() => handlePageChange('searchParameters')}>Save and continue</Button>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default DataParametersForm;
