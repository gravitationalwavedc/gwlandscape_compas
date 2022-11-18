import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';
import {fryerSupernovaEngineOptions, remnantMassPrescriptionOptions, kickVelocityDistributionOptions}
    from '../../Utils/parameters';
import SelectInput from './Atoms/SelectInput';


const SupernovaKickParametersForm = ({formik}) => {
    const [showFryerSupernovaEngine, setShowFryerSupernovaEngine] = useState(true);
    const [showVelocity, setShowVelocity] = useState(false);


    const handleRemnantMassPrescriptionOnChange = (e) => {
        formik.setFieldValue('remnantMassPrescription', e.target.value);
        setShowFryerSupernovaEngine(e.target.value === 'FRYER2012');
    };

    const handleKickVelocityDistChange = (e) => {
        formik.setFieldValue('kickVelocityDistribution', e.target.value);
        setShowVelocity(e.target.value === 'FIXED');
    };

    return (
        <React.Fragment>
            <Row>
                <Col md={5}>
                    <SelectInput
                        formik={formik}
                        title='Remnant Mass Prescription'
                        name='remnantMassPrescription'
                        type='string'
                        help=''
                        options={remnantMassPrescriptionOptions}
                        onChange={handleRemnantMassPrescriptionOnChange}
                    />
                </Col>
                <Col md={5}>
                    <SelectInput
                        formik={formik}
                        show={showFryerSupernovaEngine}
                        title='Fryer Supernova Engine'
                        name='fryerSupernovaEngine'
                        type='string'
                        help=''
                        options={fryerSupernovaEngineOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={5}>
                    <SelectInput
                        formik={formik}
                        title='Kick Velocity Distribution'
                        name='kickVelocityDistribution'
                        type='string'
                        help=''
                        options={kickVelocityDistributionOptions}
                        onChange={handleKickVelocityDistChange}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={5}>
                    <Input
                        formik={formik}
                        title="Velocity 1 (km/s)"
                        name="velocity1"
                        type="number"
                        data-testid="velocity1"
                        show={showVelocity}
                        help=""
                    />
                </Col>
                <Col md={5}>
                    <Input
                        formik={formik}
                        title="Velocity 2 (km/s)"
                        name="velocity2"
                        data-testid="velocity2"
                        type="number"
                        show={showVelocity}
                        help=""
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default SupernovaKickParametersForm;