import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';
import {fryerSupernovaEngineOptions, remnantMassPrescriptionOptions, kickVelocityDistributionOptions}
    from '../../Utils/parameters';
import SelectInput from './Atoms/SelectInput';


const SupernovaKickParametersForm = ({formik}) => {
    const [showFryerSupernovaEngine, setShowFryerSupernovaEngine] = useState(true);

    const handleRemnantMassPrescriptionOnChange = (e) => {
        formik.setFieldValue('remnantMassPrescription', e.target.value);
        setShowFryerSupernovaEngine(e.target.value === 'FRYER2012');
    };

    return (
        <React.Fragment>
            <Row>
                <Col>
                    <h2>Supernova Remnant and Kick Parameters</h2>
                </Col>
            </Row>
            <Row>
                <Col>
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
                <Col>
                    <SelectInput
                        formik={formik}
                        show={showFryerSupernovaEngine}
                        title='Fryer Supernova Engine'
                        name='fryerSupernovaEngine'
                        type='string'
                        help='Supernova engine type if using the fallback prescription from Fryer et al. (2012)'
                        options={fryerSupernovaEngineOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <SelectInput
                        formik={formik}
                        title='Kick Velocity Distribution'
                        name='kickVelocityDistribution'
                        type='string'
                        help='Natal kick magnitude distribution'
                        options={kickVelocityDistributionOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Velocity 1 (km/s)"
                        name="velocity1"
                        type="number"
                        help="Value to be used as the (drawn) kick magnitude for the primary star of a
                        binary system when evolving in BSE mode, should the star undergo a supernova event
                        (km s −1 ), Value > 0"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Velocity 2 (km/s)"
                        name="velocity2"
                        type="number"
                        help="Value to be used as the (drawn) kick magnitude for the second star of a
                        binary system when evolving in BSE mode, should the star undergo a supernova event
                        (km s −1 ), Value > 0"
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default SupernovaKickParametersForm;