import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';

const initialMassFn = [
    {'value': 'SALPETER', 'label': 'SALPETER'},
    {'value': 'POWERLAW', 'label': 'POWERLAW'},
    {'value': 'UNIFORM', 'label': 'UNIFORM'},
    {'value': 'KROUPA', 'label': 'KROUPA'},
];

const massRatioDist = [
    {'value': 'FLAT', 'label': 'FLAT'},
    {'value': 'DUQUENNOYMAYOR1991', 'label': 'DUQUENNOYMAYOR1991'},
    {'value': 'SANA2012', 'label': 'SANA2012'},
];

const semiMajorAxisDist = [
    {'value': 'FLATINLOG', 'label': 'FLATINLOG'},
    {'value': 'DUQUENNOYMAYOR1991', 'label': 'DUQUENNOYMAYOR1991'},
    {'value': 'SANA2012', 'label': 'SANA2012'},
];

const metallicityDist = [
    {'value': 'ZSOLAR', 'label': 'ZSOLAR'},
    {'value': 'LOGUNIFORM', 'label': 'LOGUNIFORM'},
];

const InitialParametersForm = ({formik}) => {

    const [showMassPower, setShowMassPower] = useState(false);
    const [showMassRatios, setShowMassRatios] = useState(true);
    const [showSeparations, setShowSeparations] = useState(true);
    const [showOrbitalPeriods, setShowOrbitalPeriods] = useState(false);
    const [showMetallicities, setShowMetallicities] = useState(false);

    const handleInitialMassFnOnChange = (e) => {
        let value = e.target.value;
        formik.setFieldValue('initialMassFunction', value);
        if(value === 'POWERLAW'){
            setShowMassPower(true);
        } else {
            setShowMassPower(false);
        }
    };

    const handleMassRatioDistributionOnChange = (e) => {
        let value = e.target.value;
        formik.setFieldValue('massRatioDistribution', value);
        if(value === 'FLAT'){
            setShowMassRatios(true);
        } else {
            setShowMassRatios(false);
        }
    };

    const handleSemiMajorAxisDistOnChange = (e) => {
        let value = e.target.value;
        formik.setFieldValue('semiMajorAxisDistribution', value);
        if(['FLATINLOG', 'DUQUENNOYMAYOR1991'].includes(value)){
            setShowSeparations(true);
            setShowOrbitalPeriods(false);
        } else {
            setShowSeparations(false);
            setShowOrbitalPeriods(true);
        }
    };

    const handleMetallicityDistOnChange = (e) => {
        let value = e.target.value;
        formik.setFieldValue('metallicityDistribution', value);
        if(value === 'ZSOLAR'){
            setShowMetallicities(false);
        } else {
            setShowMetallicities(true);
        }
    };

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
                    <SelectInput
                        formik={formik}
                        title='Initial Mass Function'
                        name='initialMassFunction'
                        type='string'
                        help=''
                        options={initialMassFn}
                        onChange={handleInitialMassFnOnChange}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Initial Mass Power"
                        name="intialMassPower"
                        type="number"
                        show={showMassPower}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Initial Mass"
                        name="minInitialMass"
                        type="number"
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Initial Mass"
                        name="maxInitialMass"
                        type="number"
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <SelectInput
                        formik={formik}
                        title='Mass Ratio Distribution'
                        name='massRatioDistribution'
                        type='string'
                        help=''
                        options={massRatioDist}
                        onChange={handleMassRatioDistributionOnChange}
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
                        show={showMassRatios}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Mass Ratio"
                        name="maxMassRatio"
                        type="number"
                        show={showMassRatios}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <SelectInput
                        formik={formik}
                        title='Semi Major Axis Distribution'
                        name='semiMajorAxisDistribution'
                        type='string'
                        help=''
                        options={semiMajorAxisDist}
                        onChange={handleSemiMajorAxisDistOnChange}
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
                        show={showSeparations}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
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
                        formik={formik}
                        title="Min Orbital Period (Hours)"
                        name="minOrbitalPeriod"
                        type="number"
                        show={showOrbitalPeriods}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Orbital Period (Hours)"
                        name="maxOrbitalPeriod"
                        type="number"
                        show={showOrbitalPeriods}
                    />
                </Col>
            </Row>
            <Row>
                {/*<Col>*/}
                {/*    <Input*/}
                {/*        formik={formik}*/}
                {/*        title="Metallicity Distribution"*/}
                {/*        name="metallicityDistribution"*/}
                {/*        type="string"*/}
                {/*    />*/}
                {/*</Col>*/}
                <Col md={6}>
                    <SelectInput
                        formik={formik}
                        title='Metallicity Distribution'
                        name='metallicityDistribution'
                        type='string'
                        help=''
                        options={metallicityDist}
                        onChange={handleMetallicityDistOnChange}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <Input
                        formik={formik}
                        title="Min Metallicity"
                        name="minMetallicity"
                        type="number"
                        show={showMetallicities}
                    />
                </Col>
                <Col>
                    <Input
                        formik={formik}
                        title="Max Metallicity"
                        name="maxMetallicity"
                        type="number"
                        show={showMetallicities}
                    />
                </Col>
            </Row>

        </React.Fragment>
    );
};

export default InitialParametersForm;
