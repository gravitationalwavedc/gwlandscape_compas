import React from 'react';
import { Col, Row } from 'react-bootstrap';
import Input from './Atoms/Input';
import {
    fryerSupernovaEngineOptions,
    remnantMassPrescriptionOptions,
    kickVelocityDistributionOptions,
} from '../../Utils/parameters';
import SelectInput from './Atoms/SelectInput';
import { useFormikContext } from 'formik';

const SupernovaKickParametersForm = () => {
    const { values } = useFormikContext();
    const showFryerSupernovaEngine = values['remnantMassPrescription'] === 'FRYER2012';
    const showVelocity = values['kickVelocityDistribution'] === 'FIXED';

    return (
        <React.Fragment>
            <Row>
                <Col md={5}>
                    <SelectInput
                        title="Remnant Mass Prescription"
                        name="remnantMassPrescription"
                        options={remnantMassPrescriptionOptions}
                    />
                </Col>
                <Col md={5}>
                    <SelectInput
                        show={showFryerSupernovaEngine}
                        title="Fryer Supernova Engine"
                        name="fryerSupernovaEngine"
                        options={fryerSupernovaEngineOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={5}>
                    <SelectInput
                        title="Kick Velocity Distribution"
                        name="kickVelocityDistribution"
                        options={kickVelocityDistributionOptions}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={5}>
                    <Input
                        title="Velocity 1 (km/s)"
                        name="velocity1"
                        type="number"
                        data-testid="velocity1"
                        show={showVelocity}
                    />
                </Col>
                <Col md={5}>
                    <Input
                        title="Velocity 2 (km/s)"
                        name="velocity2"
                        data-testid="velocity2"
                        type="number"
                        show={showVelocity}
                    />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default SupernovaKickParametersForm;
