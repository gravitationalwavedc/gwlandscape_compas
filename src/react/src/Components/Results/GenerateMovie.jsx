import { useState, useEffect } from 'react';
import { commitMutation } from 'relay-runtime';
import { graphql } from 'react-relay';
import environment from '../../environment.js';
import { Button, Spinner } from 'react-bootstrap';
import { Formik } from 'formik';
import FormButtons from '../Forms/FormButtons.jsx';
import GenerateMovieForm from '../Forms/GenerateMovieForm.jsx';

const submitMutation = graphql`
    mutation GenerateMovieMutation($input: SingleBinaryJobMovieMutationInput!) {
        newSingleBinaryMovie(input: $input) {
            result {
                movieFilePath
            }
        }
    }
`;

const messages = [
    'Generating VIMES Movie',
    'Please wait while we process your request',
    'This may take a few minutes',
];

const GenerateMovie = ({ jobId }) => {
    const [movieFile, setMovieFile] = useState('');
    const [movieFileName, setMovieFileName] = useState('');
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [disableButtons, setDisableButtons] = useState(false);
    const [messageIndex, setMessageIndex] = useState(0);

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
        setMovieFile('');
        setMovieFileName('');
        setIsLoadingOutput(false);
        setDisableButtons(false);
    };

    const handleGenerateMovie = ({ scaling, images }) => {
        // Reset errors if any
        setOutputError('');
        setMovieFile('');
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
                } else if (response.newSingleBinaryMovie.result.movieFilePath === '') {
                    handleError('Movie file failed to generate and returned an empty string');
                } else {
                    try {
                        setMovieFile(
                            `${import.meta.env.VITE_BACKEND_URL}${response.newSingleBinaryMovie.result.movieFilePath}`,
                        );
                        setMovieFileName(`${scaling}_${images}_movie.mp4`);
                        setIsLoadingOutput(false);
                        setDisableButtons(false);
                    } catch (error) {
                        handleError(`${error.name}: ${error.message}`);
                    }
                }
            },
        });
    };

    const handleDownload = async (movieFileName) => {
        const res = await fetch(movieFile);
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
            {movieFile && (
                <>
                    <Button variant="link" onClick={() => handleDownload(movieFileName)}>
                        Download VIMES Movie
                    </Button>
                    <video key={movieFile} width="1008" height="800" controls>
                        <source src={movieFile} type="video/mp4" />
                    </video>
                </>
            )}
        </>
    );
};

export default GenerateMovie;
