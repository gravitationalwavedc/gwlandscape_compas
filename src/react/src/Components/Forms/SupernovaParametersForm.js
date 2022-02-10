import React, {useState} from 'react';
import {Col, Form, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';

const remnantMassPrescriptionOptions = [
    {'value': 'HURLEY2000', 'label': 'HURLEY2000'},
    {'value': 'BELCZYNSKI2002', 'label': 'BELCZYNSKI2002'},
    {'value': 'FRYER2012', 'label': 'FRYER2012'},
    {'value': 'MULLER2016', 'label': 'MULLER2016'},
    {'value': 'MULLERMANDEL', 'label': 'MULLERMANDEL'},
];
const fryerSupernovaEngineOptions = [
    {'value': 'DELAYED', 'label': 'DELAYED'},
    {'value': 'RAPID', 'label': 'RAPID'},
];

const blackHoleKicksOptions = [
    {'value': 'FULL', 'label': 'FULL'},
    {'value': 'REDUCED', 'label': 'REDUCED'},
    {'value': 'ZERO', 'label': 'ZERO'},
    {'value': 'FALLBACK', 'label': 'FALLBACK'},
];

const kickVelocityDistributionOptions = [
    {'value': 'ZERO', 'label': 'ZERO'},
    {'value': 'FIXED', 'label': 'FIXED'},
    {'value': 'FLAT', 'label': 'FLAT'},
    {'value': 'MAXWELLIAN', 'label': 'MAXWELLIAN'},
    {'value': 'BRAYELDRIDGE', 'label': 'BRAYELDRIDGE'},
    {'value': 'MULLER2016', 'label': 'MULLER2016'},
    {'value': 'MULLER2016MAXWELLIAN', 'label': 'MULLER2016MAXWELLIAN'},
    {'value': 'MULLERMANDEL', 'label': 'MULLERMANDEL'},
];

const pulsationalPairInstabilityPrescriptionOptions = [
    {'value': 'COMPAS', 'label': 'COMPAS'},
    {'value': 'STARTRACK', 'label': 'STARTRACK'},
    {'value': 'MARCHANT', 'label': 'MARCHANT'},
];

const SupernovaParametersForm = ({formik}) => {
    const [showFryerSupernovaEngine, setShowFryerSupernovaEngine] = useState(true);
    const [pisn, setPisn] = useState(formik.values['pairInstabilitySupernovae']);
    const [ppi, setPpi] = useState(formik.values['pulsationalPairInstabilitySupernovae']);
    const handleRemnantMassPrescriptionOnChange = (e) => {
        // console.log("value", e.target.value);
        formik.setFieldValue('remnantMassPrescription', e.target.value);
        setShowFryerSupernovaEngine(e.target.value === 'FRYER2012');
    };
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Supernova Parameters">
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Remnant Mass Prescription'
                                    name='remnantMassPrescription'
                                    type='string'
                                    help='--remnant-mass-prescription: Remnant mass prescription'
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
                                    help='--fryer-supernova-engine: Supernova engine type if using the fallback prescription from Fryer et al. (2012)'
                                    options={fryerSupernovaEngineOptions}
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Black Hole Kicks'
                                    name='blackHoleKicks'
                                    type='string'
                                    help='--black-hole-kicks: Black hole kicks relative to NS kicks'
                                    options={blackHoleKicksOptions}
                                />
                            </Col>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Kick Velocity Distribution'
                                    name='kickVelocityDistribution'
                                    type='string'
                                    help='--kick-magnitude-distribution: Natal kick magnitude distribution'
                                    options={kickVelocityDistributionOptions}
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Kick Velocity Sigma CCSN NS (km/s)"
                                    name="kickVelocitySigmaCcsnNs"
                                    type="number"
                                    help="--kick-magnitude-sigma-CCSN-NS: Sigma for chosen kick magnitude distribution for neutron stars (km s − 1 ), Value > 0"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="kick Velocity Sigma CCSN BH (km/s)"
                                    name="kickVelocitySigmaCcsnBh"
                                    type="number"
                                    help="--kick-magnitude-sigma-CCSN-BH: Sigma for chosen kick magnitude distribution for black holes (km s − 1 ), Value > 0"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Kick Velocity Sigma ECSN (km/s)"
                                    name="kickVelocitySigmaEcsn"
                                    type="number"
                                    help="--kick-magnitude-sigma-ECSN: Sigma for chosen kick magnitude distribution for ECSN (km s − 1 ), Value > 0"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Kick Velocity Sigma USSN (km/s)"
                                    name="kickVelocitySigmaUssn"
                                    type="number"
                                    help="--kick-magnitude-sigma-USSN: Sigma for chosen kick magnitude distribution for USSN (km s − 1 ), Value > 0"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Form.Group controlId="pairInstabilitySupernovae">
                                    <Form.Check
                                        custom
                                        id="pairInstabilitySupernovae"
                                        type="checkbox"
                                        name="pairInstabilitySupernovae"
                                        label="Pair Instability Supernovae"
                                        checked={pisn}
                                        value={pisn}
                                        // onChange={formik.handleChange}
                                        onChange={(e) => {
                                            // console.log('value' + e.target.checked);
                                            setPisn(e.target.checked);
                                            formik.setFieldValue('pairInstabilitySupernovae', e.target.checked);
                                        }}
                                    />
                                    <Form.Text>--pair-instability-supernovae: Enable pair instability supernovae (PISN)</Form.Text>
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="PISN Lower Limit (M&#9737;)"
                                    name="pisnLowerLimit"
                                    type="number"
                                    help="--pisn-lower-limit: Minimum core mass for PISN, Value > 0"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="PISN Upper Limit (M&#9737;)"
                                    name="pisnUpperLimit"
                                    type="number"
                                    help="--pisn-upper-limit: Maximum core mass for PISN, 0 < Value > --pisn-lower-limit"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Form.Group controlId="pulsationalPairInstabilitySupernovae">
                                    <Form.Check
                                        custom
                                        id="pulsationalPairInstabilitySupernovae"
                                        type="checkbox"
                                        name="pulsationalPairInstabilitySupernovae"
                                        label="Pulsational Pair Instability Supernovae"
                                        checked={ppi}
                                        value={ppi}
                                        // onChange={formik.handleChange}
                                        onChange={(e) => {
                                            // console.log('value' + e.target.checked);
                                            setPpi(e.target.checked);
                                            formik.setFieldValue('pulsationalPairInstabilitySupernovae',e.target.checked);
                                        }}
                                    />
                                    <Form.Text>--pulsational-pair-instability: Enable mass loss due to pulsational-pair-instability (PPI)</Form.Text>
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="PPI Lower Limit (M&#9737;)"
                                    name="ppiLowerLimit"
                                    type="number"
                                    help="--ppi-lower-limit: Minimum core mass for PPI, Value > 0"
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="PPI Upper Limit (M&#9737;)"
                                    name="ppiUpperLimit"
                                    type="number"
                                    help="--ppi-upper-limit: Maximum core mass for PPI, 0 < Value > --ppi-lower-limit"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Pulsational Pair Instability Prescription'
                                    name='pulsationalPairInstabilityPrescription'
                                    type='string'
                                    help='--pulsational-pair-instability-prescription: Pulsational pair instability prescriptionn'
                                    options={pulsationalPairInstabilityPrescriptionOptions}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Maximum Neutron Star Mass (M&#9737;)"
                                    name="maximumNeutronStarMass"
                                    type="number"
                                    help="--maximum-neutron-star-mass: Maximum mass of a neutron star, Value > 0"
                                />
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default SupernovaParametersForm;
