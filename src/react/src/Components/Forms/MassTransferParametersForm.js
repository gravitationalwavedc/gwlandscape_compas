import React from 'react';
import {Col, Form, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';
import SelectInput from "./Atoms/SelectInput";

const massTransferAngularMomentumLossPrescriptionOptions = [
    {'value': 'JEANS', 'label': 'JEANS'},
    {'value': 'ISOTROPIC', 'label': 'ISOTROPIC'},
    {'value': 'CIRCUMBINARY', 'label': 'CIRCUMBINARY'},
    {'value': 'ARBITRARY', 'label': 'ARBITRARY'},
];

const massTransferAccertionEfficiencyPrescriptionOptions = [
    {'value': 'THERMAL', 'label': 'THERMAL'},
    {'value': 'FIXED', 'label': 'FIXED'},
];

const MassTransferParametersForm = ({formik}) => {

    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Common Envelope Parameters">
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Angular Momentum Loss Prescription'
                                    name='massTransferAngularMomentumLossPrescription'
                                    type='string'
                                    help='--mass-transfer-angular-momentum-loss-prescription: Mass Transfer Angular Momentum Loss prescription'
                                    options={massTransferAngularMomentumLossPrescriptionOptions}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Fraction Accreted"
                                    name="massTransferFa"
                                    type="number"
                                    help="--mass-transfer-fa: Mass Transfer fraction accreted in FIXED prescription, value > 0"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Accertion Efficiency Prescription'
                                    name='massTransferAccertionEfficiencyPrescription'
                                    type='string'
                                    help='--mass-transfer-accretion-efficiency-prescription: Mass transfer accretion efficiency prescription'
                                    options={massTransferAccertionEfficiencyPrescriptionOptions}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="JLoss"
                                    name="massTransferJloss"
                                    type="number"
                                    help="--mass-transfer-jloss: Specific angular momentum with which the non-accreted system leaves the system, value > 0"
                                />
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default MassTransferParametersForm;
