import React from 'react';
import { Col, Row } from 'react-bootstrap';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';
import {
    massTransferAccretionEfficiencyPrescriptionOptions,
    massTransferAngularMomentumLossPrescriptionOptions,
    lambdaPrescriptionOptions,
} from '../../Utils/parameters';
import { useFormikContext } from 'formik';

const MassTransferCEParametersForm = () => {
    const { values } = useFormikContext();
    const showMassTransferFA = values['massTransferAccretionEfficiencyPrescription'] === 'FIXED';

    return (
        <React.Fragment>
            <Row>
                <Col md={6}>
                    <SelectInput
                        title="Angular Momentum Loss Prescription"
                        name="massTransferAngularMomentumLossPrescription"
                        type="string"
                        options={massTransferAngularMomentumLossPrescriptionOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <SelectInput
                        title="Accretion Efficiency Prescription"
                        name="massTransferAccretionEfficiencyPrescription"
                        options={massTransferAccretionEfficiencyPrescriptionOptions}
                    />
                </Col>
                <Col>
                    <Input show={showMassTransferFA} title="Fraction Accreted" name="massTransferFa" type="number" />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input title="Alpha" name="commonEnvelopeAlpha" type="number" />
                </Col>
                <Col>
                    <SelectInput
                        title="Lambda Prescription"
                        name="commonEnvelopeLambdaPrescription"
                        options={lambdaPrescriptionOptions}
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default MassTransferCEParametersForm;
