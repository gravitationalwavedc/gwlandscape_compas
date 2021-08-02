import React, { useState } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import { Container, Col, Row, Tab, Nav } from 'react-bootstrap';
import { useFormik } from 'formik'; 
import JobTitle from '../Components/Forms/JobTitle';
import DataForm from '../Components/Forms/DataForm';
import DataParametersForm from '../Components/Forms/DataParametersForm';
import SearchParametersForm from '../Components/Forms/SearchParametersForm';
import ReviewJob from '../Components/Forms/ReviewJob';
import initialValues from '../Components/Forms/initialValues';
import validationSchema from '../Components/Forms/validationSchema';

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
    const [key, setKey] = useState('data');

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
                    private: false, 
                },
                data: {
                    dataChoice: values.dataChoice,
                    sourceDataset: values.sourceDataset,
                },
                dataParameters: {
                    startFrequencyBand: values.startFrequencyBand,
                    minStartTime: values.minStartTime,
                    maxStartTime: values.maxStartTime,
                    asini: values.asini,
                    freqBand: values.freqBand,
                    alpha: values.alpha,
                    delta: values.delta,
                    orbitTp: values.orbitTp,
                    orbitPeriod: values.orbitPeriod,
                    driftTime: values.driftTime,
                    dFreq: values.dFreq,
                },
                searchParameters: {
                    searchStartTime: values.searchStartTime,
                    searchTBlock: values.searchTBlock,
                    searchCentralA0: values.searchCentralA0,
                    searchA0Band: values.searchA0Band,
                    searchA0Bins: values.searchA0Bins,
                    searchCentralP: values.searchCentralP,
                    searchPBand: values.searchPBand,
                    searchPBins: values.searchPBins,
                    searchCentralOrbitTp: values.searchCentralOrbitTp,
                    searchOrbitTpBand: values.searchOrbitTpBand,
                    searchOrbitTpBins: values.searchOrbitTpBins,
                    searchLLThreshold: values.searchLLThreshold
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
        <Container fluid>
            <Row>
                <Col md={2}/>
                <Col md={8} style={{minHeight: '110px'}}>
                    <JobTitle formik={formik} />
                </Col>
            </Row>
            <Tab.Container id="jobForm" activeKey={key} onSelect={(key) => setKey(key)}>
                <Row>
                    <Col md={2}>
                        <Nav className="flex-column">
                            <Nav.Item>
                                <Nav.Link eventKey="data">
                                    <h5>Data</h5>
                                    <p>Data source type</p>
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link eventKey="dataParameters">
                                    <h5>Atom Parameters</h5>
                                    <p>Atom generation parameters</p>
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link eventKey="searchParameters">
                                    <h5>Search Parameters</h5>
                                    <p>Compas search configuration</p>
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link eventKey="review">
                                    <h5>Review</h5>
                                    <p>Finalise and start your job</p>
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Col>
                    <Col md={8}>
                        <Tab.Content>
                            <Tab.Pane eventKey="data">
                                <DataForm formik={formik} handlePageChange={setKey}/>
                            </Tab.Pane>
                            <Tab.Pane data-testid="dataParametersPane" eventKey="dataParameters">
                                <DataParametersForm formik={formik} handlePageChange={setKey}/>
                            </Tab.Pane>
                            <Tab.Pane eventKey="searchParameters">
                                <SearchParametersForm formik={formik} handlePageChange={setKey}/>
                            </Tab.Pane>
                            <Tab.Pane eventKey="review">
                                <ReviewJob 
                                    formik={formik} 
                                    values={formik.values} 
                                    handleSubmit={formik.handleSubmit}/>
                            </Tab.Pane>
                        </Tab.Content>
                    </Col>
                </Row>
            </Tab.Container>
        </Container>
    );
};

NewJob.defaultProps = {
    initialValues: initialValues
};

export default NewJob;
