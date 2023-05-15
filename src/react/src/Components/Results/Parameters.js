import React from 'react';
import {graphql,  createFragmentContainer} from 'react-relay';
import { Row, Col} from 'react-bootstrap';
import ParameterTableRow from './ParameterTableRow';

const Parameters = (props) =>
    <React.Fragment>
        <Row>
            <Col>
                <h2 className="mb-md-3 mt-md-2">Basic Options</h2>
            </Col>
        </Row>
        <ParameterTableRow params={[
            {name: 'Number of Systems', value: props.jobData.numberOfSystems},
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Initial Mass Function', value: props.jobData.initialMassFunction},
            {name: 'Initial Mass Power', value: props.jobData.initialMassPower}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Min Initial Mass', value: props.jobData.minInitialMass},
            {name: 'Max Initial Mass', value: props.jobData.maxInitialMass}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Mass Ratio Distribution', value: props.jobData.massRatioDistribution},
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Min Mass Ratio', value: props.jobData.minMassRatio},
            {name: 'Max Mass Ratio', value: props.jobData.maxMassRatio}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Semi Major Axis Distribution', value: props.jobData.semiMajorAxisDistribution},
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Min Semi Major Axis (AU)', value: props.jobData.minSemiMajorAxis},
            {name: 'Max Semi Major Axis (AU)', value: props.jobData.maxSemiMajorAxis}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Min Orbital Period (Hours)', value: props.jobData.minOrbitalPeriod},
            {name: 'Max Orbital Period (Hours)', value: props.jobData.maxOrbitalPeriod}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Metallicity Distribution', value: props.jobData.metallicityDistribution},
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Min Metallicity', value: props.jobData.minMetallicity},
            {name: 'Max Metallicity', value: props.jobData.maxMetallicity}
        ]}/>

        <Row>
            <Col>
                <h2 className="mb-md-3 mt-md-3">Supernova - Kick Options</h2>
            </Col>
        </Row>
        <ParameterTableRow params={[
            {name: 'Remnant Mass Prescription', value: props.jobData.remnantMassPrescription},
            {name: 'Fryer Supernova Engine', value: props.jobData.fryerSupernovaEngine}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Kick Velocity Distribution', value: props.jobData.kickVelocityDistribution},
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Velocity 1 (km/s)', value: props.jobData.velocity1},
            {name: 'Velocity 2 (km/s)', value: props.jobData.velocity2}
        ]}/>
        <Row>
            <Col>
                <h2 className="mb-md-3 mt-md-3">Mass Transfer - CE Options</h2>
            </Col>
        </Row>
        <ParameterTableRow params={[
            {
                name: 'Angular Momentum Loss Prescription',
                value: props.jobData.massTransferAngularMomentumLossPrescription
            },
            {name: '', value: ''}
        ]}/>
        <ParameterTableRow params={[
            {
                name: 'Accretion Efficiency Prescription',
                value: props.jobData.massTransferAccretionEfficiencyPrescription
            },
            {name: 'Fraction Accreted', value: props.jobData.massTransferFa}
        ]}/>
        <ParameterTableRow params={[
            {name: 'Alpha', value: props.jobData.commonEnvelopeAlpha},
            {name: 'Lambda Prescription', value: props.jobData.commonEnvelopeLambdaPrescription}
        ]}/>
    </React.Fragment>;


export default createFragmentContainer(Parameters, {
    jobData: graphql`
        fragment Parameters_jobData on CompasJobNode {
            numberOfSystems
            minInitialMass
            maxInitialMass
            initialMassFunction
            initialMassPower
            metallicityDistribution
            minMetallicity
            maxMetallicity
            minMassRatio
            maxMassRatio
            massRatioDistribution
            minSemiMajorAxis
            maxSemiMajorAxis
            semiMajorAxisDistribution
            minOrbitalPeriod
            maxOrbitalPeriod
            massTransferAngularMomentumLossPrescription
            massTransferAccretionEfficiencyPrescription
            massTransferFa
            commonEnvelopeAlpha
            commonEnvelopeLambdaPrescription
            remnantMassPrescription
            fryerSupernovaEngine
            kickVelocityDistribution
            velocity1
            velocity2
        }
    `
});