import React, {useState} from 'react';
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

const MassTransferParametersForm = ({formik, collapsed, onTitleClick}) => {
    const [showMassTransferFa, setShowMassTransferFa] = useState(false);
    const [showMassTransferJloss, setshowMassTransferJloss] = useState(false);

    const handleAngularMomentumLossPrescriptionOnChange = (e) => {
        formik.setFieldValue('massTransferAngularMomentumLossPrescription', e.target.value);
        setshowMassTransferJloss(e.target.value === 'ARBITRARY');
    };

    const handleAccertionEfficiencyPrescriptionOnChange = (e) => {
        formik.setFieldValue('massTransferAccertionEfficiencyPrescription', e.target.value);
        setShowMassTransferFa(e.target.value === 'FIXED');
    };

    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Mass Transfer Parameters" collapsed={collapsed} onTitleClick={onTitleClick}>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Angular Momentum Loss Prescription'
                                    name='massTransferAngularMomentumLossPrescription'
                                    type='string'
                                    help='--mass-transfer-angular-momentum-loss-prescription: Mass Transfer Angular
                                    Momentum Loss prescription'
                                    options={massTransferAngularMomentumLossPrescriptionOptions}
                                    onChange={handleAngularMomentumLossPrescriptionOnChange}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    show={showMassTransferJloss}
                                    title="Specific Angular Momentum Lost"
                                    name="massTransferJloss"
                                    type="number"
                                    help="--mass-transfer-jloss: Specific angular momentum with which the non-accreted
                                    system leaves the system, value > 0"
                                />
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Accretion Efficiency Prescription'
                                    name='massTransferAccertionEfficiencyPrescription'
                                    type='string'
                                    help='--mass-transfer-accretion-efficiency-prescription: Mass transfer accretion
                                    efficiency prescription'
                                    options={massTransferAccertionEfficiencyPrescriptionOptions}
                                    onChange={handleAccertionEfficiencyPrescriptionOnChange}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    show={showMassTransferFa}
                                    title="Fraction Accreted"
                                    name="massTransferFa"
                                    type="number"
                                    help="--mass-transfer-fa: Mass Transfer fraction accreted in FIXED prescription,
                                    value > 0"
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
