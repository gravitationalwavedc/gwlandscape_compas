import React, { useState } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import { Container, Col, Row, Tab, Nav } from 'react-bootstrap';
import { useFormik } from 'formik';
// import JobTitle from '../Components/Forms/JobTitle';
// import DataForm from '../Components/Forms/DataForm';
// import DataParametersForm from '../Components/Forms/DataParametersForm';
// import SearchParametersForm from '../Components/Forms/SearchParametersForm';
import BasicParametersForm from '../Components/Forms/BasicParametersForm';
import KickParametersForm from '../Components/Forms/KickParametersForm';
// import ReviewJob from '../Components/Forms/ReviewJob';
import initialValues from '../Components/Forms/initialValues';
import validationSchema from '../Components/Forms/validationSchema';
import ReviewSingleBinaryJob from '../Components/Forms/ReviewSingleBinaryJob';
import JobOutput from '../Components/Results/JobOutput';

const submitMutation = graphql`
  mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
    newSingleBinary(input: $input) {
      result {
        jobId
        gridFilePath
        plotFilePath
        vanPlotFilePath
        runDetailsPath
      }
    }
  }
`;

const NewSingleBinaryJob = ({initialValues, router, ...props}) => {
    const [key, setKey] = useState('basicParameters');

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: values => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    const [gridFile, setGridFile] = useState('');
    const [plotFile, setPlotFile] = useState('');
    const [vanPlotFile, setVanPlotFile] = useState('');
    const [runDetails, setRunDetails] = useState('');

    const handleJobSubmission = (values) => {
        // The mutation requires all number values to be strings.
        // Object.entries(values)
        //     .filter(([key, value]) => typeof(value) === 'number')
        //     .map(([key, value]) => values[key] = value.toString());

        const variables = {
            input: {
                mass1: values.mass1,
                mass2: values.mass2,
                metallicity: values.metallicity,
                eccentricity: values.eccentricity,
                separation: values.separation,
                orbitalPeriod: values.orbitPeriod,
                velocityRandomNumber1: values.velocityRandomNumber1,
                velocityRandomNumber2: values.velocityRandomNumber2,
                velocity1: values.velocity1,
                velocity2: values.velocity2,
                theta1: values.theta1,
                theta2: values.theta2,
                phi1: values.phi1,
                phi2: values.phi2,
                meanAnomaly1: values.meanAnomaly1,
                meanAnomaly2: values.meanAnomaly2,
            }
        };

        // setGridFile(gridFile + ' Eman ');
        // setPlotFile('http://127.0.0.1:8003/files/jobs/64/COMPAS_Output/Detailed_Output/gw151226evol.png');

        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: (response, errors) => {
                if (!errors) {
                    // router.replace(`/compas/job-results/${response.newCompasJob.result.jobId}/`);
                    console.log('all done');
                    console.log(response);

                    setTimeout( () => {
                        setGridFile('http://localhost:8003' + response.newSingleBinary.result.gridFilePath);
                        setPlotFile('http://localhost:8003' + response.newSingleBinary.result.plotFilePath);
                        setVanPlotFile('http://localhost:8003' + response.newSingleBinary.result.vanPlotFilePath);
                        setRunDetails('http://localhost:8003' + response.newSingleBinary.result.runDetailsPath);
                    },6000);
                }
            },
        });
    };

    return (
        <Container fluid>
            <Row>
                <Col md={4}>
                    <BasicParametersForm formik={formik}/>
                    <KickParametersForm formik={formik}/>

                    <ReviewSingleBinaryJob
                        formik={formik}
                        values={formik.values}
                        handleSubmit={formik.handleSubmit}/>
                </Col>
                <Col md={8}>
                    <JobOutput
                        gridfileName={gridFile}
                        detailedplotfilename={plotFile}
                        vanplotfilename={vanPlotFile}
                        rundetails={runDetails}
                    />
                </Col>
            </Row>
        </Container>
    );
};

NewSingleBinaryJob.defaultProps = {
    initialValues: initialValues
};

export default NewSingleBinaryJob;