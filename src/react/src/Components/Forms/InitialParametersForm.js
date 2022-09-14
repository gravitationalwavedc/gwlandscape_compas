import React from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';

const InitialParametersForm = ({formik}) => {
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <h2>Population</h2>
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
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Initial Mass (M&#9737;)"
                        name="minInitialMass"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Initial Mass (M&#9737;)"
                        name="maxInitialMass"
                        type="number"
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Input
                        formik={formik}
                        title="Initial Mass Function"
                        name="initialMassFunction"
                        type="string"
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Metallicity"
                        name="metallicity"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Metallicity Distribution"
                        name="metallicityDistribution"
                        type="string"
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Metallicity (Z&#9737;)"
                        name="minMetallicity"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Metallicity (Z&#9737;)"
                        name="maxMetallicity"
                        type="number"
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Mass Ratio"
                        name="minMassRatio"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Mass Ratio"
                        name="maxMassRatio"
                        type="number"
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Input
                        formik={formik}
                        title="Mass Ratio Distribution"
                        name="massRatioDistribution"
                        type="string"
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Semi Major Axis (AU)"
                        name="minSemiMajorAxis"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Semi Major Axis (AU)"
                        name="maxSemiMajorAxis"
                        type="number"
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Input
                        formik={formik}
                        title="Semi Major Axis Distribution"
                        name="semiMajorAxisDistribution"
                        type="string"
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default InitialParametersForm;
