import React from 'react';
import { Col, Row } from 'react-bootstrap';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';
import { useFormikContext } from 'formik';

const initialMassFn = [
    { value: 'SALPETER', label: 'SALPETER' },
    { value: 'POWERLAW', label: 'POWERLAW' },
    { value: 'UNIFORM', label: 'UNIFORM' },
    { value: 'KROUPA', label: 'KROUPA' },
];

const massRatioDist = [
    { value: 'FLAT', label: 'FLAT' },
    { value: 'DUQUENNOYMAYOR1991', label: 'DUQUENNOYMAYOR1991' },
    { value: 'SANA2012', label: 'SANA2012' },
];

const semiMajorAxisDist = [
    { value: 'FLATINLOG', label: 'FLATINLOG' },
    { value: 'DUQUENNOYMAYOR1991', label: 'DUQUENNOYMAYOR1991' },
    { value: 'SANA2012', label: 'SANA2012' },
];

const metallicityDist = [
    { value: 'ZSOLAR', label: 'ZSOLAR' },
    { value: 'LOGUNIFORM', label: 'LOGUNIFORM' },
];

const InitialParametersForm = () => {
    const { values } = useFormikContext();
    const showMassPower = values['initialMassFunction'] === 'POWERLAW';
    const showMassRatios = values['massRatioDistribution'] === 'FLAT';
    const showSeparations = ['FLATINLOG', 'DUQUENNOYMAYOR1991'].includes(values['semiMajorAxisDistribution']);
    const showMetallicities = values['metallicityDistribution'] !== 'ZSOLAR';

    return (
        <React.Fragment>
            <Row>
                <Col>
                    <h2>Population</h2>
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Input title="Number of Systems" name="numberOfSystems" type="number" />
                </Col>
            </Row>
            <Row>
                <Col>
                    <SelectInput title="Initial Mass Function" name="initialMassFunction" options={initialMassFn} />
                </Col>
                <Col>
                    <Input title="Initial Mass Power" name="initialMassPower" type="number" show={showMassPower} />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input title="Min Initial Mass" name="minInitialMass" type="number" />
                </Col>
                <Col>
                    <Input title="Max Initial Mass" name="maxInitialMass" type="number" />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <SelectInput
                        title="Mass Ratio Distribution"
                        name="massRatioDistribution"
                        options={massRatioDist}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input title="Min Mass Ratio" name="minMassRatio" type="number" show={showMassRatios} />
                </Col>
                <Col>
                    <Input title="Max Mass Ratio" name="maxMassRatio" type="number" show={showMassRatios} />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <SelectInput
                        title="Semi Major Axis Distribution"
                        name="semiMajorAxisDistribution"
                        options={semiMajorAxisDist}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        title="Min Semi Major Axis (AU)"
                        name="minSemiMajorAxis"
                        type="number"
                        show={showSeparations}
                    />
                </Col>
                <Col>
                    <Input
                        title="Max Semi Major Axis (AU)"
                        name="maxSemiMajorAxis"
                        type="number"
                        show={showSeparations}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        title="Min Orbital Period (Hours)"
                        name="minOrbitalPeriod"
                        type="number"
                        show={!showSeparations}
                    />
                </Col>
                <Col>
                    <Input
                        title="Max Orbital Period (Hours)"
                        name="maxOrbitalPeriod"
                        type="number"
                        show={!showSeparations}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <SelectInput
                        title="Metallicity Distribution"
                        name="metallicityDistribution"
                        options={metallicityDist}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input title="Min Metallicity" name="minMetallicity" type="number" show={showMetallicities} />
                </Col>
                <Col>
                    <Input title="Max Metallicity" name="maxMetallicity" type="number" show={showMetallicities} />
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default InitialParametersForm;
