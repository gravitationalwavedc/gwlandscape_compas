import React, { useState } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import { Container, Col, Row, Tab, Nav } from 'react-bootstrap';
import { useFormik } from 'formik';
import BasicParametersForm from '../Components/Forms/BasicParametersForm';
import KickParametersForm from '../Components/Forms/KickParametersForm';
import CommonEnvelopeParametersForm from '../Components/Forms/CommonEnvelopeParametersForm';
import SupernovaParametersForm from '../Components/Forms/SupernovaParametersForm';
import MassTransferParametersForm from '../Components/Forms/MassTransferParametersForm';
import ReviewSingleBinaryJob from '../Components/Forms/ReviewSingleBinaryJob';
import JobOutput from '../Components/Results/JobOutput';
import initialValues from '../Components/Forms/initialValues';
import validationSchema from '../Components/Forms/validationSchema';

const submitMutation = graphql`
  mutation NewSingleBinaryJobMutation($input: SingleBinaryJobMutationInput!) {
    newSingleBinary(input: $input) {
      result {
        jobId
        gridFilePath
        plotFilePath
        vanPlotFilePath
        detailedOutputFilePath
      }
    }
  }
`;

// const checkFileExist = (urlToFile, timeout=3000) => {
//     return new Promise((resolve, reject) => {
//         if(urlToFile == ''){
//             reject(new Error('Plot was not created successfully'));
//         }
//         let timer = setTimeout(() => {
//             reject(new Error('Plot was not created successfully'));
//         }, timeout);
//
//         let xhr = new XMLHttpRequest();
//         let exist = false;
//         while (!exist) {
//             xhr.open('HEAD', urlToFile, false);
//             xhr.send();
//
//             if (xhr.status != '404') {
//                 exist = true;
//             }
//         }
//         clearTimeout(timer);
//         resolve(true);
//     });
// };

const checkFileExist = (urlToFile) => {
    let xhr = new XMLHttpRequest();

    xhr.open('HEAD', urlToFile, false);
    xhr.send();

    return (xhr.status != '404')? true : false;
};

const NewSingleBinaryJob = ({initialValues, router, ...props}) => {

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: values => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    // const [gridFile, setGridFile] = useState('');
    const [plotFile, setPlotFile] = useState('');
    const [vanPlotFile, setVanPlotFile] = useState('');
    const [detailedOutputFile, setDetailedOutputFile] = useState('');
    const [vanPlotLoaded, setVanPlotLoaded] = useState(false);
    const [detailedPlotLoaded, setDetailedPlotLoaded] = useState(false);
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);

    const handleJobSubmission = (values) => {
        setIsLoadingOutput(true);
        scrollTo(0, 0);

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
                commonEnvelopeAlpha: values.commonEnvelopeAlpha,
                commonEnvelopeLambdaPrescription: values.commonEnvelopeLambdaPrescription,
                commonEnvelopeLambda: values.commonEnvelopeLambda,
                remnantMassPrescription: values.remnantMassPrescription,
                fryerSupernovaEngine: values.fryerSupernovaEngine,
                blackHoleKicks: values.blackHoleKicks,
                kickVelocityDistribution: values.kickVelocityDistribution,
                kickVelocitySigmaCcsnNs: values.kickVelocitySigmaCcsnNs,
                kickVelocitySigmaCcsnBh: values.kickVelocitySigmaCcsnBh,
                kickVelocitySigmaEcsn: values.kickVelocitySigmaEcsn,
                kickVelocitySigmaUssn: values.kickVelocitySigmaUssn,
                pairInstabilitySupernovae: Boolean(values.pairInstabilitySupernovae),
                pisnLowerLimit: values.pisnLowerLimit,
                pisnUpperLimit: values.pisnUpperLimit,
                pulsationalPairInstabilitySupernovae: Boolean(values.pulsationalPairInstabilitySupernovae),
                ppiLowerLimit: values.ppiLowerLimit,
                ppiUpperLimit: values.ppiUpperLimit,
                pulsationalPairInstabilityPrescription: values.pulsationalPairInstabilityPrescription,
                maximumNeutronStarMass: values.maximumNeutronStarMass,
                massTransferAngularMomentumLossPrescription: values.massTransferAngularMomentumLossPrescription,
                massTransferAccertionEfficiencyPrescription: values.massTransferAccertionEfficiencyPrescription,
                massTransferFa: values.massTransferFa,
                massTransferJloss: values.massTransferJloss,
            }
        };


        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: async (response, errors) => {
                if (!errors && (response.newSingleBinary.result.vanPlotFilePath!='')) {
                    console.log('No errors');

                    // router.replace(`/compas/job-results/${response.newCompasJob.result.jobId}/`);
                    // console.log('all done');
                    // console.log(response);

                    const myinterval = setInterval(() => {
                        if((!vanPlotLoaded) && checkFileExist('http://localhost:8003' + response.newSingleBinary.result.vanPlotFilePath)){
                            setVanPlotFile('http://localhost:8003' + response.newSingleBinary.result.vanPlotFilePath);
                            setVanPlotLoaded(true);
                        }

                        if((!detailedPlotLoaded) && checkFileExist('http://localhost:8003' + response.newSingleBinary.result.plotFilePath)){
                            setPlotFile('http://localhost:8003' + response.newSingleBinary.result.plotFilePath);
                            setDetailedPlotLoaded(true);
                        }

                        // setGridFile('http://localhost:8003' + response.newSingleBinary.result.gridFilePath);
                        setDetailedOutputFile('http://localhost:8003' + response.newSingleBinary.result.detailedOutputFilePath);
                    }, 2000);

                    if(vanPlotLoaded && detailedPlotLoaded){
                        clearInterval(myinterval);
                        setVanPlotLoaded(false);
                        setDetailedPlotLoaded(false);
                        setIsLoadingOutput(false);
                    }
                }
                else{
                    console.log('something went wrong');
                    setOutputError('Output could not be generated');
                    setIsLoadingOutput(false);
                }
            },
        });
    };

    return (
        <Container fluid>
            <Row>
                <Col md={5}>
                    <BasicParametersForm formik={formik}/>
                    <KickParametersForm formik={formik}/>
                    <CommonEnvelopeParametersForm formik={formik}/>
                    <SupernovaParametersForm formik={formik}/>
                    <MassTransferParametersForm formik={formik}/>

                    <ReviewSingleBinaryJob
                        formik={formik}
                        values={formik.values}
                        handleSubmit={formik.handleSubmit}/>
                </Col>
                <Col md={7}>
                    <JobOutput
                        // gridfileName={gridFile}
                        detailedplotfilename={plotFile}
                        vanplotfilename={vanPlotFile}
                        detailedOutputFileName={detailedOutputFile}
                        error={outputError}
                        isLoading={isLoadingOutput}
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