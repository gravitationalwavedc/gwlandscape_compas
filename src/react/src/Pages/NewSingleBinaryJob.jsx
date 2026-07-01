import { useEffect, useState } from 'react';
import { commitMutation, fetchQuery } from 'relay-runtime';
import { createFragmentContainer, graphql } from 'react-relay';
import { Container, Col, Nav, Row, Tab, Alert } from 'react-bootstrap';
import { Formik } from 'formik';
import BasicParametersForm from '../Components/Forms/BasicParametersForm';
import FormButtons from '../Components/Forms/FormButtons.jsx';
import SingleBinaryTab from '../Components/SingleBinaryTab';
import initialValues from '../Components/Forms/initialValues';
import validationSchema from '../Components/Forms/validationSchema';
import MassTransferCEParameters from '../Components/Forms/MassTransferCEParameters';
import SupernovaKickParametersForm from '../Components/Forms/SupernovaKickParametersForm';
import VanDenHeuvel from '../Components/Plots/VanDenHeuvel';
import SingleBinaryPlot from '../Components/Plots/SingleBinaryPlot';
import environment from '../environment.js';
import GenerateMovie from '../Components/Results/GenerateMovie.jsx';
import useTaskPolling from '../Utils/Hooks.jsx';

const submitMutation = graphql`
    mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
        newSingleBinary(input: $input) {
            result {
                taskId
                jobId
            }
        }
    }
`;

const singleBinaryJobQuery = graphql`
    query NewSingleBinaryJobQuery($jobId: ID!) {
        singleBinaryJob(id: $jobId) {
            plotJsonData
            detailedOutputFilePath
        }
    }
`

const NewSingleBinaryJob = ({ data }) => {
    const [detailedOutputFile, setDetailedOutputFile] = useState('');
    const [plotJsonData, setplotJsonData] = useState('');
    const [taskId, setTaskId] = useState('');
    const [jobId, setJobId] = useState('');
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [disableButtons, setDisableButtons] = useState(false);
    const [activeTab, setActiveTab] = useState('binary');

    // Poll for Celery task status
    const { task, error: pollingError } = useTaskPolling(taskId);

    // When Celery task has a status of SUCCESS, fetch data.
    // If the task has a status of FAILURE, display the error message.
    useEffect(() => {
        if (task?.status === 'SUCCESS') {
            fetchQuery(environment, singleBinaryJobQuery, { jobId }).subscribe({
                next: (response) => {
                    setplotJsonData(JSON.parse(response.singleBinaryJob.plotJsonData));
                    setDetailedOutputFile(
                        `${import.meta.env.VITE_BACKEND_URL}${response.singleBinaryJob.detailedOutputFilePath}`,
                    );
                    setIsLoadingOutput(false);
                    setDisableButtons(false);
                },
                error: (err) => {
                    handleError(`${err.name}: ${err.message}`);
                },
            });
        } else if (task?.status === 'FAILURE' || task?.status === 'TIMEOUT') {
            handleError(`Task failed with error: ${task.error}`);
        }

        if (pollingError) {
            handleError(`${pollingError.name}: ${pollingError.message}`);
        }
    }, [task, jobId, pollingError]); // eslint-disable-line react-hooks/exhaustive-deps

    const resetOutput = () => {
        setDetailedOutputFile('');
        setplotJsonData('');
        setIsLoadingOutput(false);
        setDisableButtons(false);
    };
    const handleFormReset = () => {
        resetOutput();
        setOutputError('');
    };

    const handleError = (errorMessage) => {
        setActiveTab('binary');
        setOutputError(errorMessage);
        resetOutput();
    };

    const handleJobSubmission = (values) => {
        setActiveTab('job-output');

        // Reset errors if any
        setOutputError('');

        // Reset the json data so they know something is happening.
        setplotJsonData('');

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

        commitMutation(environment, {
            mutation: submitMutation,
            variables: variables,
            onError: async (error) => {
                handleError(`${error.name}: ${error.message}`);
            },
            onCompleted: async (response, errors) => {
                if (errors) {
                    const errorMessages = errors.reduce((prev, curr) => `${prev}, ${curr.message}`, '');
                    handleError(`Output failed to generate with errors: ${errorMessages}`);
                } else {
                    setTaskId(response.newSingleBinary.result.taskId);
                    setJobId(response.newSingleBinary.result.jobId);
                }
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
            {outputError !== '' && (
                <Row className="mt-5" data-testid="error-message">
                    <Col>
                        <Alert variant="danger" dismissible onClose={() => setOutputError('')}>
                            <Alert.Heading>Something went wrong.</Alert.Heading>
                            <p>
                                Error was &quot;{outputError}&quot;. That&apos;s all we know. Please try again in a few
                                minutes.
                            </p>
                        </Alert>
                    </Col>
                </Row>
            )}
            <Tab.Container id="single-binary-tabs" activeKey={activeTab} onSelect={(tab) => setActiveTab(tab)}>
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
                            <h5 className="mt-3 mb-0">Results</h5>
                            <Nav.Item>
                                <Nav.Link eventKey="job-output" disabled={plotJsonData === ''}>
                                    {isLoadingOutput ? 'Loading...' : 'COMPAS Output'}
                                </Nav.Link>
                                {plotJsonData === '' && !isLoadingOutput && (
                                    <p className="mt-0 pt-0 text-muted">Run a simulation to see results</p>
                                )}
                            </Nav.Item>
                            <Nav.Item>
                                <p className="mt-0 pt-0 text-muted">
                                    COMPAS - {data?.compasVersion ? `v${data.compasVersion}` : 'Unknown'}
                                </p>
                            </Nav.Item>
                            <h5 className="mt-3 mb-0">Post-Processing</h5>
                            <Nav.Item>
                                <Nav.Link eventKey="generate-movie" disabled={jobId === ''}>
                                    Generate Movie
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Col>
                    <Col md={activeTab !== 'job-output' ? 6 : 10}>
                        <Tab.Content className="mt-2">
                            <Formik
                                initialValues={initialValues}
                                onSubmit={(values) => handleJobSubmission(values)}
                                onReset={handleFormReset}
                                validationSchema={validationSchema}
                            >
                                <>
                                    <SingleBinaryTab title="Binary" eventKey="binary">
                                        <BasicParametersForm />
                                    </SingleBinaryTab>
                                    <SingleBinaryTab title="Supernova & Kick" eventKey="kick">
                                        <SupernovaKickParametersForm />
                                    </SingleBinaryTab>
                                    <SingleBinaryTab title="Mass Transfer & Common Envelope" eventKey="mass-transfer">
                                        <MassTransferCEParameters />
                                    </SingleBinaryTab>
                                    {['binary', 'kick', 'mass-transfer'].includes(activeTab) && (
                                        <FormButtons
                                            submitButtonContent="Start Simulation"
                                            disableButtons={disableButtons}
                                        />
                                    )}
                                </>
                            </Formik>

                            <SingleBinaryTab title="COMPAS Output" eventKey="job-output">
                                {isLoadingOutput ? (
                                    <div>Loading...</div>
                                ) : (
                                    <>
                                        <a className="mr-4" data-testid="download-link" href={detailedOutputFile}>
                                            Download Output File
                                        </a>
                                        {plotJsonData && (
                                            <>
                                                <VanDenHeuvel data={plotJsonData} />
                                                <div className="plotContainer">
                                                    {plotJsonData?.plots.map((plotData) => (
                                                        <Col key={plotData.meta.label} className="mb-5 mt-5">
                                                            <SingleBinaryPlot className="container" data={plotData} />
                                                        </Col>
                                                    ))}
                                                </div>
                                            </>
                                        )}
                                    </>
                                )}
                            </SingleBinaryTab>
                            <SingleBinaryTab title="Generate ViMES Movie" eventKey="generate-movie">
                                {isLoadingOutput ? <div>Loading...</div> : <GenerateMovie jobId={jobId} />}
                            </SingleBinaryTab>
                        </Tab.Content>
                    </Col>
                </Row>
            </Tab.Container>
        </Container>
    );
};

export default createFragmentContainer(NewSingleBinaryJob, {
    data: graphql`
        fragment NewSingleBinaryJob_data on Query {
            compasVersion
        }
    `,
});
