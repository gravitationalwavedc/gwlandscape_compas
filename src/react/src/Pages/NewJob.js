import React, { useState } from 'react';
import {commitMutation} from 'relay-runtime';
import {graphql} from 'react-relay';
import {harnessApi} from '../index';
import {Container, Col, Row, Button} from 'react-bootstrap';
import { useFormik } from 'formik'; 
import JobTitle from '../Components/Forms/JobTitle';
import ReviewJob from '../Components/Forms/ReviewJob';
import compasJobInitialValues from '../Components/Forms/compasJobInitialValues';
// import validationSchema from '../Components/Forms/validationSchema';

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
        // validationSchema: validationSchema,
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
                    metallicity: '0.1'
                }

            }
        };

        console.log(variables);

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
                            <Button>Basic</Button>
                        </Col>
                        <Col md={9}>
                            <ReviewJob
                                formik={formik}
                                values={formik.values}
                                handleSubmit={formik.handleSubmit}/>
                        </Col>
                    </Row>
                </Container>

            </Row>
            {/*</Tab.Container>*/}
        </Container>

    );
};

NewJob.defaultProps = {
    initialValues: compasJobInitialValues
};

export default NewJob;
