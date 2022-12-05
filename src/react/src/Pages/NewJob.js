import React from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import {Container, Col, Row, Nav, Tab} from 'react-bootstrap';
import { useFormik } from 'formik'; 
import JobTitle from '../Components/Forms/JobTitle';
import ReviewJob from '../Components/Forms/ReviewJob';
import compasJobInitialValues from '../Components/Forms/compasJobInitialValues';
import InitialParametersForm from '../Components/Forms/InitialParametersForm';
import validationSchema from '../Components/Forms/compasJobValidationSchema';
import SupernovaKickParametersForm from '../Components/Forms/SupernovaKickParametersForm';
import MassTransferCEParametersForm from '../Components/Forms/MassTransferCEParameters';

const submitMutation = graphql`
  mutation NewJobMutation($input: CompasJobMutationInput!) {
    newCompasJob(input: $input) {
      result {
        jobId
      }
    }
  }
`;

const NewJob = ({initialValues, router}) => {

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: values => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    const handleJobSubmission = (values) => {
        // The mutation requires all number values to be strings.
        Object.entries(values)
            .filter(([key, value]) => typeof(value) === 'number')
            .map(([key, value]) => values[key] = value.toString());

        const variables = {
            input: {
                start: {
                    name: values.name,
                    description: values.description,
                    private: false
                },
                basicParameters: {
                    numberOfSystems: values.numberOfSystems,
                    minInitialMass: values.minInitialMass,
                    maxInitialMass: values.maxInitialMass,
                    initialMassFunction: values.initialMassFunction,
                    intialMassPower: values.intialMassPower,
                    metallicityDistribution: values.metallicityDistribution,
                    minMetallicty: values.minMetallicty,
                    maxMetallicity: values.maxMetallicity,
                    minMassRatio: values.minMassRatio,
                    maxMassRatio: values.maxMassRatio,
                    massRatioDistribution: values.massRatioDistribution,
                    minSemiMajorAxis: values.minSemiMajorAxis,
                    maxSemiMajorAxis: values.maxSemiMajorAxis,
                    semiMajorAxisDistribution: values.semiMajorAxisDistribution,
                    minOrbitalPeriod: values.minOrbitalPeriod,
                    maxOrbitalPeriod: values.maxOrbitalPeriod,
                }

            }
        };

        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: (response, errors) => {
                if (!errors) {
                    router.replace(`/compas/job-results/${response.newCompasJob.result.jobId}/`);
                }
            },
        });
    };

    return (
        <Container>
            <Row>
                <Container>
                    <Row><Col><h1 className="pt-5 mb-4">Launch COMPAS Job</h1></Col></Row>
                    <Row>
                        <Col md={6} style={{minHeight: '110px'}}>
                            <JobTitle formik={formik} />
                        </Col>
                    </Row>
                </Container>
            </Row>
            <Row>
                <Tab.Container defaultActiveKey="initialParameters">
                    <Row>
                        <Col md={4}>
                            <Nav variant="pills" className="flex-column">
                                <Nav.Item>
                                    <Nav.Link
                                        eventKey="initialParameters"
                                        className="mb-1">
                                        Basic
                                    </Nav.Link>
                                </Nav.Item>
                                <Nav.Item>
                                    <Nav.Link
                                        eventKey="supernovaKickParameters"
                                        className="mb-1">
                                        Supernova - Kick
                                    </Nav.Link>
                                </Nav.Item>
                                <Nav.Item>
                                    <Nav.Link
                                        eventKey="massTransferCEParameters"
                                        className="mb-1">
                                        Mass Transfer - CE
                                    </Nav.Link>
                                </Nav.Item>
                            </Nav>
                        </Col>
                        <Col md={8}>
                            <Tab.Content>
                                <Tab.Pane eventKey="initialParameters">
                                    <InitialParametersForm formik={formik} />
                                </Tab.Pane>
                                <Tab.Pane eventKey="supernovaKickParameters">
                                    <SupernovaKickParametersForm formik={formik} />
                                </Tab.Pane>
                                <Tab.Pane eventKey="massTransferCEParameters">
                                    <MassTransferCEParametersForm formik={formik} />
                                </Tab.Pane>
                            </Tab.Content>
                        </Col>
                    </Row>
                </Tab.Container>
            </Row>
            <Row>
                <Col md={2}>  </Col>
                <Col md={7}>
                    <ReviewJob
                        formik={formik}
                        values={formik.values}
                        handleSubmit={formik.handleSubmit}
                        handleReset={formik.resetForm}/>
                </Col>
            </Row>
        </Container>
    );
};

NewJob.defaultProps = {
    initialValues: compasJobInitialValues
};

export default NewJob;
