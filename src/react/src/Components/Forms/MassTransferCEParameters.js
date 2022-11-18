import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';
import {massTransferAccretionEfficiencyPrescriptionOptions,
    massTransferAngularMomentumLossPrescriptionOptions,
    lambdaPrescriptionOptions} from '../../Utils/parameters';

const MassTransferCEParametersForm = ({formik}) => {
    const [showMassTransferFA, setShowMassTransferFA] = useState(false);

    const handleAccretionEfficiencyPrescriptionOnChange = (e) => {
        formik.setFieldValue('massTransferAccretionEfficiencyPrescription', e.target.value);
        setShowMassTransferFA(e.target.value === 'FIXED');
    };

    return (
        <React.Fragment>
            <Row>
                <Col md={6}>
                    <SelectInput
                        formik={formik}
                        title='Angular Momentum Loss Prescription'
                        name='massTransferAngularMomentumLossPrescription'
                        type='string'
                        help=''
                        options={massTransferAngularMomentumLossPrescriptionOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <SelectInput
                        formik={formik}
                        title='Accretion Efficiency Prescription'
                        name='massTransferAccretionEfficiencyPrescription'
                        type='string'
                        help=''
                        options={massTransferAccretionEfficiencyPrescriptionOptions}
                        onChange={handleAccretionEfficiencyPrescriptionOnChange}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        show={showMassTransferFA}
                        title="Fraction Accreted"
                        name="massTransferFa"
                        type="number"
                        help=""
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Alpha"
                        name="commonEnvelopeAlpha"
                        type="number"
                        help=""
                    />
                </Col>
                <Col>
                    <SelectInput
                        formik={formik}
                        title='Lambda Prescription'
                        name='commonEnvelopeLambdaPrescription'
                        type='string'
                        help=''
                        options={lambdaPrescriptionOptions}
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default MassTransferCEParametersForm;