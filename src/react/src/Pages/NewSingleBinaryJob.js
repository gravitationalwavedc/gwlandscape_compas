import React, { useState } from 'react';
import { commitMutation } from 'relay-runtime';
import { graphql } from 'react-relay';
import { harnessApi } from '../index';
import { Container, Col, Nav, Row, Tab } from 'react-bootstrap';
import { useFormik } from 'formik';
import BasicParametersForm from '../Components/Forms/BasicParametersForm';
import ReviewJob from '../Components/Forms/ReviewJob';
import SingleBinaryTab from '../Components/SingleBinaryTab';
import initialValues from '../Components/Forms/initialValues';
import validationSchema from '../Components/Forms/validationSchema';
import JobOutput from '../Components/Results/JobOutput';
import MassTransferCEParameters from '../Components/Forms/MassTransferCEParameters';
import SupernovaKickParametersForm from '../Components/Forms/SupernovaKickParametersForm';
import RenderMassContainer from '../Components/Plots/RenderMassContainer';
import RenderLengthContainer from '../Components/Plots/RenderLengthContainer';
import RenderHRDiagramContainer from '../Components/Plots/RenderHRDiagramContainer';
import VanDenHeuvel from '../Components/Plots/VanDenHeuvel';

const submitMutation = graphql`
    mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
        newSingleBinary(input: $input) {
            result {
                jobId
                jsonData
                detailedOutputFilePath
            }
        }
    }
`;

const IS_DEV = !process.env.NODE_ENV || process.env.NODE_ENV === 'development';

const server_url = IS_DEV ? 'http://localhost:8003' : 'https://gwlandscape.org.au';

const NewSingleBinaryJob = () => {
    const [detailedOutputFile, setDetailedOutputFile] = useState('');
    const [jsonData, setJsonData] = useState('');
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [disableButtons, setDisableButtons] = useState(false);

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: (values) => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    let syncId = 1;

    const handleFormReset = () => {
        formik.resetForm();
        setDetailedOutputFile('');
        setJsonData('');
        setIsLoadingOutput(false);
        setOutputError('');
        setDisableButtons(false);
    };

    const handleJobSubmission = (values) => {
        // Reset errors if any
        setOutputError('');

        // Reset the json data so they know something is happening.
        setJsonData('');

        // We don't want to update the Formik values to null because
        // it causes errors with uncontrolled components.
        const valuesCopy = { ...values };

        // But graphql expects null instead of ''.
        Object.keys(valuesCopy).forEach((key) => {
            if (valuesCopy[key] === '') {
                valuesCopy[key] = null;
            }
        });

        setDetailedOutputFile('');
        setIsLoadingOutput(true);
        setDisableButtons(true);

        const variables = {
            input: {
                mass1: valuesCopy.mass1,
                mass2: valuesCopy.mass2,
                metallicity: valuesCopy.metallicity,
                eccentricity: valuesCopy.eccentricity,
                separation: valuesCopy.separation,
                orbitalPeriod: valuesCopy.orbitalPeriod,
                velocity1: valuesCopy.velocity1,
                velocity2: valuesCopy.velocity2,
                commonEnvelopeAlpha: valuesCopy.commonEnvelopeAlpha,
                commonEnvelopeLambdaPrescription: valuesCopy.commonEnvelopeLambdaPrescription,
                remnantMassPrescription: valuesCopy.remnantMassPrescription,
                fryerSupernovaEngine: valuesCopy.fryerSupernovaEngine,
                massTransferAngularMomentumLossPrescription: valuesCopy.massTransferAngularMomentumLossPrescription,
                massTransferAccretionEfficiencyPrescription: valuesCopy.massTransferAccretionEfficiencyPrescription,
                massTransferFa: valuesCopy.massTransferFa,
            },
        };

        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: async (response, errors) => {
                if (!errors && response.newSingleBinary.result.detailedOutputFilePath !== '') {
                    setJsonData(JSON.parse(response.newSingleBinary.result.jsonData));
                    setDetailedOutputFile(server_url + response.newSingleBinary.result.detailedOutputFilePath);
                } else {
                    setOutputError('Output could not be generated');
                    setDetailedOutputFile('');
                    setJsonData('');
                }
                setIsLoadingOutput(false);
                setDisableButtons(false);
            },
        });
    };

    return (
        <Container fluid>
            <Row className="mt-5">
                <Col>
                    <h1>Simulate the evolution of a binary</h1>
                    <h5>
                        Run a simulation of an evolution of a specific binary. Detailed plots will be automatically
                        generated using COMPAS and available to download.
                    </h5>
                </Col>
            </Row>
            <Tab.Container id="single-binary-tabs" defaultActiveKey="binary">
                <Row className="mt-4">
                    <Col md={2}>
                        <Nav fill variant="pills" className="flex-column text-center">
                            <Nav.Item>
                                <Nav.Link eventKey="binary">Binary</Nav.Link>
                            </Nav.Item>
                            <h5 className="mt-3 mb-0">Advanced settings</h5>
                            <Nav.Item>
                                <Nav.Link eventKey="kick">Supernova & Kick</Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link eventKey="mass-transfer">
                                    Mass Transfer &<br />
                                    Common Envelope
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Col>
                    <Col md={4}>
                        <Tab.Content className="mt-2">
                            <SingleBinaryTab title="Binary" eventKey="binary">
                                <BasicParametersForm formik={formik} />
                            </SingleBinaryTab>
                            <SingleBinaryTab title="Supernova & Kick" eventKey="kick">
                                <SupernovaKickParametersForm formik={formik} />
                            </SingleBinaryTab>
                            <SingleBinaryTab title="Mass Transfer & Common Envelope" eventKey="mass-transfer">
                                <MassTransferCEParameters formik={formik} />
                            </SingleBinaryTab>
                        </Tab.Content>
                        <ReviewJob
                            formik={formik}
                            values={formik.values}
                            handleSubmit={formik.handleSubmit}
                            handleReset={handleFormReset}
                            disableButtons={disableButtons}
                        />
                    </Col>
                    <Col md={6}>
                        <JobOutput
                            detailedOutputFileName={detailedOutputFile}
                            error={outputError}
                            isLoading={isLoadingOutput}
                        />
                        {jsonData && (
                            <>
                                <VanDenHeuvel data={jsonData} />
                                <div className="plotContainer">
                                    <Col className="mb-5 mt-5">
                                        <RenderMassContainer className="container" syncId={syncId} data={jsonData} />
                                    </Col>
                                    <Col className="mb-5">
                                        <RenderLengthContainer className="container" syncId={syncId} data={jsonData} />
                                    </Col>
                                    <Col className="mb-5">
                                        <RenderHRDiagramContainer
                                            className="container"
                                            syncId={syncId}
                                            data={jsonData}
                                        />
                                    </Col>
                                </div>
                            </>
                        )}
                    </Col>
                </Row>
            </Tab.Container>
        </Container>
    );
};

export default NewSingleBinaryJob;
