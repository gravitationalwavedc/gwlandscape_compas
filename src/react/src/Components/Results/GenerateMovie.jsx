import { useState, useEffect } from 'react';
import { commitMutation, fetchQuery } from 'relay-runtime';
import { graphql } from 'react-relay';
import environment from '../../environment.js';
import { Button, Spinner } from 'react-bootstrap';
import { Formik } from 'formik';
import FormButtons from '../Forms/FormButtons.jsx';
import GenerateMovieForm from '../Forms/GenerateMovieForm.jsx';
import useTaskPolling from '../../Utils/Hooks.jsx';

const submitMutation = graphql`
    mutation GenerateMovieMutation($input: SingleBinaryJobMovieMutationInput!) {
        newSingleBinaryMovie(input: $input) {
            result {
                taskId
            }
        }
    }
`;

const singleBinaryJobMovieQuery = graphql`
    query GenerateMovieQuery($jobId: ID!, $scaling: String, $images: String) {
        singleBinaryJob(id: $jobId) {
            movieFileUrl(scaling: $scaling, images: $images)
        }
    }
`;

const messages = [
    'Generating VIMES Movie',
    'Please wait while we process your request',
    'This may take a few minutes',
];

const GenerateMovie = ({ jobId }) => {
    const [movieFileUrl, setMovieFileUrl] = useState('');
    const [movieFileName, setMovieFileName] = useState('');
    const [taskId, setTaskId] = useState('');
    const [submittedValues, setSubmittedValues] = useState(null);
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [disableButtons, setDisableButtons] = useState(false);
    const [messageIndex, setMessageIndex] = useState(0);

    // Poll for Celery task status
    const { task, error: pollingError } = useTaskPolling(taskId);

    // When Celery task has a status of SUCCESS, fetch data.
    // If the task has a status of FAILURE, display the error message.
    useEffect(() => {
        if (!submittedValues) return;

        if (task?.status === 'SUCCESS') {
            fetchQuery(environment, singleBinaryJobMovieQuery, { jobId, ...submittedValues }).subscribe({
                next: (response) => {
                    setMovieFileUrl(
                        `${import.meta.env.VITE_BACKEND_URL}${response.singleBinaryJob.movieFileUrl}`,
                    );
                    setMovieFileName(`${submittedValues.scaling}_${submittedValues.images}_movie.mp4`);
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
    }, [task, jobId, pollingError, submittedValues]);

    useEffect(() => {
        if (!isLoadingOutput) return;
        if (messageIndex >= messages.length - 1) return;

        const timeout = setTimeout(() => {
            setMessageIndex((prev) => prev + 1);
        }, 3000);

        return () => clearTimeout(timeout);
    }, [messageIndex, isLoadingOutput]);

    const handleError = (errorMessage) => {
        setOutputError(errorMessage);
        setMovieFileUrl('');
        setMovieFileName('');
        setIsLoadingOutput(false);
        setDisableButtons(false);
    };

    const handleGenerateMovie = ({ scaling, images }) => {
        // Reset errors if any
        setOutputError('');
        setMovieFileUrl('');
        setMovieFileName('');
        setIsLoadingOutput(true);
        setDisableButtons(true);

        const variables = {
            input: {
                jobId: jobId,
                scaling: scaling,
                images: images,
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
                    handleError(`Movie failed to generate with errors: ${errorMessages}`);
                } else {
                    setSubmittedValues({ scaling, images });
                    setTaskId(response.newSingleBinaryMovie.result.taskId);
                }
            },
        });
    };

    const handleDownload = async (movieFileName) => {
        const res = await fetch(movieFileUrl);
        const blob = await res.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = movieFileName;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <>
            <p>
                Generate a movie using{' '}
                <a href="https://github.com/layabinu/VIMES_VIsualization_of_Massive_Evolving_Stars">ViMES</a>{' '}
                (Visualisation of Massive Evolving Stars). This tool takes in the detailed output from COMPAS and
                creates a movie displaying the evolution of a single binary. The generated movie will be available for
                download once it is ready.
            </p>
            <Formik
                initialValues={{ scaling: 'log', images: 'default' }}
                onSubmit={(values) => handleGenerateMovie(values)}
            >
                <>
                    <GenerateMovieForm />
                    <FormButtons
                        submitButtonContent={
                            isLoadingOutput ? (
                                <>
                                    <Spinner animation="border" size="sm" />
                                    <span className="dots" style={{ marginLeft: '0.5rem' }}>
                                        {messages[messageIndex]}
                                    </span>
                                </>
                            ) : (
                                'Generate VIMES Movie'
                            )
                        }
                        showReset={false}
                        disableButtons={disableButtons}
                    />
                </>
            </Formik>
            {outputError && <div className="error">{outputError}</div>}
            {movieFileUrl && (
                <>
                    <Button variant="link" onClick={() => handleDownload(movieFileName)}>
                        Download VIMES Movie
                    </Button>
                    <video key={movieFileUrl} width="1008" height="800" controls>
                        <source src={movieFileUrl} type="video/mp4" />
                    </video>
                </>
            )}
        </>
    );
};

export default GenerateMovie;
