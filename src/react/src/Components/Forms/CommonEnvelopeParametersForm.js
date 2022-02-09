import React from 'react';
import {Col, Form, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';
import SelectInput from "./Atoms/SelectInput";

const CommonEnvelopeParametersForm = ({formik}) => {
    // const testOptions = [
    //     {'value': 'value1', 'label': 'Label 1'},
    //     {'value': 'value2', 'label': 'Label 2'},
    // ]

    const lambdaPrescriptionOptions = [
        {'value': 'LAMBDA_FIXED', 'label': 'LAMBDA_FIXED'},
        {'value': 'LAMBDA_LOVERIDGE', 'label': 'LAMBDA_LOVERIDGE'},
        {'value': 'LAMBDA_NANJING', 'label': 'LAMBDA_NANJING'},
        {'value': 'LAMBDA_KRUCKOW', 'label': 'LAMBDA_KRUCKOW'},
        {'value': 'LAMBDA_DEWI', 'label': 'LAMBDA_DEWI'},
    ];
    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Common Envelope Parameters">
                        <Row>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Alpha"
                                    name="commonEnvelopeAlpha"
                                    type="number"
                                    help="--common-envelope-alpha: Common Envelope efficiency alpha, Value > 0"
                                />
                            </Col>
                            <Col>

                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                {/*<Input*/}
                                {/*    formik={formik}*/}
                                {/*    title="Lambda Prescription"*/}
                                {/*    name="commonEnvelopeLambdaPrescription"*/}
                                {/*    type="number"*/}
                                {/*    help="--common-envelope-lambda-prescription: CE lambda prescription"*/}
                                {/*/>*/}

                                {/*<Form.Group controlId="commonEnvelopeLambdaPrescription">*/}
                                {/*    <Form.Label>Lambda Prescription</Form.Label>*/}
                                {/*    <Form.Control*/}
                                {/*        name="commonEnvelopeLambdaPrescription"*/}
                                {/*        as="select"*/}
                                {/*        custom*/}
                                {/*        {...formik.getFieldProps('commonEnvelopeLambdaPrescription')}>*/}
                                {/*        {lambdaPrescriptionOptions.map(({value, label}) =>*/}
                                {/*            <option value={value} key={value}>{label}</option>*/}
                                {/*        )}*/}
                                {/*    </Form.Control>*/}
                                {/*    <Form.Text>--common-envelope-lambda-prescription: CE lambda prescription</Form.Text>*/}
                                {/*    <Form.Control.Feedback type='invalid'>*/}
                                {/*        {formik.errors[name]}*/}
                                {/*    </Form.Control.Feedback>*/}
                                {/*</Form.Group>*/}

                                <SelectInput
                                    formik={formik}
                                    title='Lambda Prescription'
                                    name='commonEnvelopeLambdaPrescription'
                                    type='string'
                                    help='--common-envelope-lambda-prescription: CE lambda prescription'
                                    options={lambdaPrescriptionOptions}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    title="Lambda"
                                    name="commonEnvelopeLambda"
                                    type="number"
                                    help="--common-envelope-lambda: Common Envelope lambda, Value > 0"
                                />
                            </Col>
                        </Row>
                    </FormCard>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default CommonEnvelopeParametersForm;
