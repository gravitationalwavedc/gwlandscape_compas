import React from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import {Container, Col, Row, Button} from 'react-bootstrap';
import { useFormik } from 'formik'; 
import JobTitle from '../Components/Forms/JobTitle';
import ReviewJob from '../Components/Forms/ReviewJob';
import compasJobInitialValues from '../Components/Forms/compasJobInitialValues';
import InitialParametersForm from '../Components/Forms/InitialParametersForm';

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
                    metallicity: values.metallicity,
                    metallicityDistribution: values.metallicityDistribution,
                    minMetallicty: values.minMetallicty,
                    maxMetallicity: values.maxMetallicity,
                    minMassRatio: values.minMassRatio,
                    maxMassRatio: values.maxMassRatio,
                    massRatioDistribution: values.massRatioDistribution,
                    minSemiMajorAxis: values.minSemiMajorAxis,
                    maxSemiMajorAxis: values.maxSemiMajorAxis,
                    semiMajorAxisDistribution: values.semiMajorAxisDistribution
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
            <h1 className="pt-5 mb-4">
                Launch COMPAS Job
            </h1>
            <Row>
                <Col md={6} style={{minHeight: '110px'}}>
                    <JobTitle formik={formik} />
                </Col>
            </Row>
            <Row>
                <Container>
                    <Row>
                        <Col md={3}>
                            <Button
                                className="mb-1"
                                variant="primary"
                                size="md"
                                block
                            >
                                Basic
                            </Button>
                            <Button
                                className="btn-secondary"
                                size="md"
                                block
                            >
                                Kick
                            </Button>
                        </Col>
                        <Col md={9}>
                            <InitialParametersForm formik={formik} />
                            <ReviewJob
                                formik={formik}
                                values={formik.values}
                                handleSubmit={formik.handleSubmit}
                                handleReset={formik.resetForm}
                            />
                        </Col>
                    </Row>
                </Container>

            </Row>
        </Container>
    );
};

NewJob.defaultProps = {
    initialValues: compasJobInitialValues
};

export default NewJob;
