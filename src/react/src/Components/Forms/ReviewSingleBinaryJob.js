import React, {useState} from 'react';
import {Button, Col, Row} from 'react-bootstrap';

const ReviewSingleBinaryJob = ({handleSubmit, formik, handleReset}) => {
    const [errors, setErrors] = useState([]);

    const submitReview = async () => {
        const errors = await formik.validateForm();
        setErrors(Object.values(errors));

        if (Object.keys(errors).length === 0 && errors.constructor === Object) {
            handleSubmit();
        }
    };

    return <>
        <Row className="mb-5">
            <Col md={4}>
                <Button onClick={submitReview} variant='form' className='w-100'>Start Simulation</Button>
            </Col>
            <Col md={{span: 4, offset: 4}}>
                <Button onClick={handleReset} variant='form' className='w-100'>Reset Form</Button>
            </Col>
        </Row>
        <Row className="mb-5">
            <ul>{errors.map(value => <li className="text-danger" key={value}>{value}</li>)}</ul>
        </Row>
    </>;
};

ReviewSingleBinaryJob.defaultProps = {
    handleSubmit: null
};

export default ReviewSingleBinaryJob;
