import React, {useState} from 'react';
import {Col, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';
import SelectInput from './Atoms/SelectInput';

const lambdaPrescriptionOptions = [
    {'value': 'LAMBDA_FIXED', 'label': 'LAMBDA_FIXED'},
    {'value': 'LAMBDA_LOVERIDGE', 'label': 'LAMBDA_LOVERIDGE'},
    {'value': 'LAMBDA_NANJING', 'label': 'LAMBDA_NANJING'},
    {'value': 'LAMBDA_KRUCKOW', 'label': 'LAMBDA_KRUCKOW'},
    {'value': 'LAMBDA_DEWI', 'label': 'LAMBDA_DEWI'},
];

const CommonEnvelopeParametersForm = ({formik}) => {
    const [showLambda, setShowLambda] = useState(false);
    const handleLambdaPrescriptionOnChange = (e) => {
        // console.log("value", e.target.value);
        formik.setFieldValue('commonEnvelopeLambdaPrescription', e.target.value);
        setShowLambda(e.target.value === 'LAMBDA_FIXED');
    };

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
                            <Col/>
                        </Row>
                        <Row>
                            <Col>
                                <SelectInput
                                    formik={formik}
                                    title='Lambda Prescription'
                                    name='commonEnvelopeLambdaPrescription'
                                    type='string'
                                    help='--common-envelope-lambda-prescription: CE lambda prescription'
                                    options={lambdaPrescriptionOptions}
                                    onChange={handleLambdaPrescriptionOnChange}
                                />
                            </Col>
                            <Col>
                                <Input
                                    formik={formik}
                                    show={showLambda}
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
