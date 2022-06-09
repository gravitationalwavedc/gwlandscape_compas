import React from 'react';
import {Col, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';

const BasicParametersForm = ({formik, collapsed, onTitleClick}) => {
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Initial Parameters" collapsed={collapsed} onTitleClick={onTitleClick}>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Mass 1 (M&#9737;)"
                                    name="mass1"
                                    type="number"
                                    help="Mass of the initially more massive star.  0 < Value < 150"
                                />

                                <Input
                                    formik={formik}
                                    title="Metallicity (Z&#9737;)"
                                    name="metallicity"
                                    type="number"
                                    help="Metallicity of stars.  1E-4 < Value < 0.03"
                                />
                                <Input
                                    formik={formik}
                                    title="Separation (AU)"
                                    name="separation"
                                    data-testid="separation"
                                    type="number"
                                    help="Value > 0. Only used with no Orbital Period"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Mass 2 (M&#9737;)"
                                    name="mass2"
                                    type="number"
                                    help="Mass of the initially less massive star. 0 < Value < 150"
                                />
                                <Input
                                    formik={formik}
                                    title="Eccentricity"
                                    name="eccentricity"
                                    type="number"
                                    help="Orbital eccentricity of the binary. 0 <= Value < 1"
                                />
                                <Input
                                    formik={formik}
                                    title="Orbital Period (days)"
                                    name="orbitalPeriod"
                                    data-testid="orbitalPeriod"
                                    type="number"
                                    help="Value > 0. Only used with no Separation"
                                />
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default BasicParametersForm;
