import React, { useState, useEffect } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import { Container, Col, Row} from 'react-bootstrap';
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

const checkFileExist = (urlToFile) => {
    let xhr = new XMLHttpRequest();

    xhr.open('HEAD', urlToFile, false);
    xhr.send();

    return (xhr.status != '404')? true : false;
};

const IS_DEV = !process.env.NODE_ENV || process.env.NODE_ENV === 'development';


const server_url = IS_DEV ? 'http://localhost:8003' : 'https://gwlandscape.org.au';

const NewSingleBinaryJob = ({initialValues}) => {

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: values => handleJobSubmission(values),
        validationSchema: validationSchema,
    });

    const [plotFile, setPlotFile] = useState('');
    const [vanPlotFile, setVanPlotFile] = useState('');
    const [detailedOutputFile, setDetailedOutputFile] = useState('');
    const [vanPlotLoaded, setVanPlotLoaded] = useState(false);
    const [detailedPlotLoaded, setDetailedPlotLoaded] = useState(false);
    const [outputError, setOutputError] = useState('');
    const [isLoadingOutput, setIsLoadingOutput] = useState(false);
    const [isBasicCollapsed, setIsBasicCollapsed] = useState(false);
    const [isKickCollapsed, setIsKickCollapsed] = useState(true);
    const [isCECollapsed, setIsCECollapsed] = useState(true);
    const [isSupernovaCollapsed, setIsSupernovaCollapsed] = useState(true);
    const [isMassTransferCollapsed, setIsMassTransferCollapsed] = useState(true);
    const [myinterval, setMyinterval] = useState(null);

    // This block that checks for plots to be loaded by checking state had to be done in useEffect. That is because
    // changing state using useState hook within setInterval won't be reflected to the component on its own
    useEffect(() => {
        if(vanPlotLoaded && detailedPlotLoaded){
            clearInterval(myinterval);
            setVanPlotLoaded(false);
            setDetailedPlotLoaded(false);
            setIsLoadingOutput(false);
        }
    }, [vanPlotLoaded, detailedPlotLoaded, isLoadingOutput]);

    const handleFormReset = () => {
        formik.resetForm();
        setVanPlotFile('');
        setDetailedOutputFile('');
        setPlotFile('');
        setIsLoadingOutput(false);
        setVanPlotLoaded(false);
        setDetailedPlotLoaded(false);
        setOutputError('');
        setIsBasicCollapsed(false);
        setIsKickCollapsed(true);
        setIsCECollapsed(true);
        setIsSupernovaCollapsed(true);
        setIsMassTransferCollapsed(true);
        setMyinterval(null);
    };
    const handleJobSubmission = (values) => {
        Object.entries(values)
            .filter(([key, value]) => value === '')
            .map(([key, value]) => values[key] = null);

        setVanPlotFile('');
        setDetailedOutputFile('');
        setPlotFile('');
        setIsLoadingOutput(true);

        scrollTo(0, 0);

        const variables = {
            input: {
                mass1: values.mass1,
                mass2: values.mass2,
                metallicity: values.metallicity,
                eccentricity: values.eccentricity,
                separation: values.separation,
                orbitalPeriod: values.orbitalPeriod,
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
                massTransferAccretionEfficiencyPrescription: values.massTransferAccretionEfficiencyPrescription,
                massTransferFa: values.massTransferFa,
                massTransferJloss: values.massTransferJloss,
            }
        };


        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: async (response, errors) => {
                if (!errors && (response.newSingleBinary.result.vanPlotFilePath!='')) {

                    setMyinterval(() => setInterval(() => {
                        if((!vanPlotLoaded) &&
                            checkFileExist(server_url + response.newSingleBinary.result.vanPlotFilePath)){
                            setVanPlotFile(server_url + response.newSingleBinary.result.vanPlotFilePath);
                            setVanPlotLoaded(true);
                        }

                        if((!detailedPlotLoaded) &&
                            checkFileExist(server_url + response.newSingleBinary.result.plotFilePath)){
                            setPlotFile(server_url + response.newSingleBinary.result.plotFilePath);
                            setDetailedPlotLoaded(true);
                        }

                        setDetailedOutputFile(server_url + response.newSingleBinary.result.detailedOutputFilePath);
                    }, 2000));
                }
                else{
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
                    <BasicParametersForm
                        formik={formik}
                        onTitleClick={()=>setIsBasicCollapsed(!isBasicCollapsed)}
                        collapsed={isBasicCollapsed}/>
                    <KickParametersForm
                        formik={formik}
                        onTitleClick={()=>setIsKickCollapsed(!isKickCollapsed)}
                        collapsed={isKickCollapsed}/>
                    <CommonEnvelopeParametersForm
                        formik={formik}
                        onTitleClick={()=>setIsCECollapsed(!isCECollapsed)}
                        collapsed={isCECollapsed}/>
                    <SupernovaParametersForm
                        formik={formik}
                        onTitleClick={()=>setIsSupernovaCollapsed(!isSupernovaCollapsed)}
                        collapsed={isSupernovaCollapsed}/>
                    <MassTransferParametersForm
                        formik={formik}
                        onTitleClick={()=>setIsMassTransferCollapsed(!isMassTransferCollapsed)}
                        collapsed={isMassTransferCollapsed}/>

                    <ReviewSingleBinaryJob
                        formik={formik}
                        values={formik.values}
                        handleSubmit={formik.handleSubmit}
                        handleReset={handleFormReset}
                    />
                </Col>
                <Col md={7}>
                    <JobOutput
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