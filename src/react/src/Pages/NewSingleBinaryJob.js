import React, { useState, useEffect } from 'react';
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

const NewSingleBinaryJob = ({ initialValues }) => {

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: values => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    const [detailedOutputFile, setDetailedOutputFile] = useState('');
    const [jsonData, setJsonData] = useState('');
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [myinterval, setMyinterval] = useState(null);
    const [disableButtons, setDisableButtons] = useState(false);
    let syncId = null; 


    const handleFormReset = () => {
        formik.resetForm();
        setDetailedOutputFile('');
        setJsonData('');
        setIsLoadingOutput(false);
        setOutputError('');
        setDisableButtons(false);
    };

    const handleJobSubmission = (values) => {
        Object.entries(values)
            .filter(([key, value]) => value === '')
            .map(([key, value]) => values[key] = null);

        setDetailedOutputFile('');
        setIsLoadingOutput(true);
        setDisableButtons(true);

        scrollTo(0, 0);

        const variables = {
            input: {
                mass1: values.mass1,
                mass2: values.mass2,
                metallicity: values.metallicity,
                eccentricity: values.eccentricity,
                separation: values.separation,
                orbitalPeriod: values.orbitalPeriod,
                velocity1: values.velocity1,
                velocity2: values.velocity2,
                commonEnvelopeAlpha: values.commonEnvelopeAlpha,
                commonEnvelopeLambdaPrescription: values.commonEnvelopeLambdaPrescription,
                remnantMassPrescription: values.remnantMassPrescription,
                fryerSupernovaEngine: values.fryerSupernovaEngine,
                massTransferAngularMomentumLossPrescription: values.massTransferAngularMomentumLossPrescription,
                massTransferAccretionEfficiencyPrescription: values.massTransferAccretionEfficiencyPrescription,
                massTransferFa: values.massTransferFa,
            }
        };


        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: async (response, errors) => {
                if(!errors && (response.newSingleBinary.result.detailedOutputFilePath !== '')) {
                    setJsonData(response.newSingleBinary.result.jsonData);
                    setDetailedOutputFile(server_url + response.newSingleBinary.result.detailedOutputFilePath);
                }
                else{
                    setOutputError('Output could not be generated');
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
                        Run a simulation of an evolution of a specific binary. 
                        Detailed plots will be automatically generated using COMPAS and available to download.
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
                                <Nav.Link eventKey="mass-transfer">Mass Transfer &<br/>Common Envelop</Nav.Link>
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
                            <SingleBinaryTab title="Mass Transfer & Common Envelop" eventKey="mass-transfer">
                                <MassTransferCEParameters formik={formik}/>
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
                        <VanDenHeuvel /> 
                        <br />
                        <div className="plotContainer">
                            <RenderMassContainer className="container" syncId={syncId} />
                            <br />
                            <RenderLengthContainer className="container" syncId={syncId} />
                            <br />
                            <br />
                            <RenderHRDiagramContainer className="container" syncId={syncId} />
                        </div>
                    </Col>
                </Row>
            </Tab.Container>
        </Container>
    );
};

NewSingleBinaryJob.defaultProps = {
    initialValues: initialValues
};

export default NewSingleBinaryJob;
