import React, { useState } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import { Container, Col, Row, Tab, Nav } from 'react-bootstrap';
import { useFormik } from 'formik'; 
import JobTitle from '../Components/Forms/JobTitle';
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
                    private: false
                }
            }
        };

        commitMutation(harnessApi.getEnvironment('compas'), {
            mutation: submitMutation,
            variables: variables,
            onCompleted: (response, errors) => {
                if (!errors) {
                    console.log(response.newCompasJob.result.jobId);
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
            <Row>
                <Col md={8}>
                    <ReviewJob
                        formik={formik}
                        values={formik.values}
                        handleSubmit={formik.handleSubmit}/>
                </Col>
            </Row>
            {/*</Tab.Container>*/}
        </Container>

    );
};

NewJob.defaultProps = {
    initialValues: initialValues
};

export default NewJob;
