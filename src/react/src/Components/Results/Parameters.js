import React from 'react';
import {graphql,  createFragmentContainer} from 'react-relay';
import { Row, Col} from 'react-bootstrap';

const Parameters = (props) =>
    <React.Fragment>
        <Row>
            <Col>
                <h2>Basic Options</h2>
            </Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Number of Systems</Col>
            <Col md={2}>{props.jobData.numberOfSystems}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Initial Mass Function</Col>
            <Col md={2}>{props.jobData.initialMassFunction}</Col>
            <Col md={4} className="paramater-name">Initial Mass Power</Col>
            <Col md={2}>{props.jobData.initialMassPower}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Min Initial Mass</Col>
            <Col md={2}>{props.jobData.minInitialMass}</Col>
            <Col md={4} className="paramater-name">Max Initial Mass</Col>
            <Col md={2}>{props.jobData.maxInitialMass}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name" className="paramater-name">Mass Ratio Distribution</Col>
            <Col md={2}>{props.jobData.massRatioDistribution}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Min Mass Ratio</Col>
            <Col md={2}>{props.jobData.minMassRatio}</Col>
            <Col md={4} className="paramater-name">Max Mass Ratio</Col>
            <Col md={2}>{props.jobData.maxMassRatio}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Semi Major Axis Distribution</Col>
            <Col md={2}>{props.jobData.semiMajorAxisDistribution}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Min Semi Major Axis (AU)</Col>
            <Col md={2}>{props.jobData.minSemiMajorAxis}</Col>
            <Col md={4} className="paramater-name">Max Semi Major Axis (AU)</Col>
            <Col md={2}>{props.jobData.maxSemiMajorAxis}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Min Orbital Period (Hours)</Col>
            <Col md={2}>{props.jobData.minOrbitalPeriod}</Col>
            <Col md={4} className="paramater-name">Max Orbital Period (Hours)</Col>
            <Col md={2}>{props.jobData.maxOrbitalPeriod}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Metallicity Distribution</Col>
            <Col md={2}>{props.jobData.metallicityDistribution}</Col>
        </Row>
        <Row>
            <Col md={4} className="paramater-name">Min Metallicity</Col>
            <Col md={2}>{props.jobData.minMetallicity}</Col>
            <Col md={4} className="paramater-name">Max Metallicity</Col>
            <Col md={2}>{props.jobData.maxMetallicity}</Col>
        </Row>
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