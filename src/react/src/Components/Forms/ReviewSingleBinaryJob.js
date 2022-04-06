import React, {useState} from 'react';
import {Button, Col, Row, Table,} from 'react-bootstrap';
import FormCard from './FormCard';

const ReviewSingleBinaryJob = ({values, handleSubmit, formik}) => {
    const [errors, setErrors] = useState([]);

    const submitReview = async () => {
        const errors = await formik.validateForm();
        setErrors(Object.values(errors));

        if (Object.keys(errors).length === 0 && errors.constructor === Object) {
            handleSubmit();
        }
    };

    return (
        <React.Fragment>
            {handleSubmit && <Row className="mb-5">
                <Col md={3}>
                    <Button onClick={submitReview}>Submit your job</Button>
                </Col>
                <Col>
                    <ul>{errors.map(value => <li className="text-danger" key={value}>{value}</li>)}</ul>
                </Col>
            </Row>}
        </React.Fragment>
    );
};

ReviewSingleBinaryJob.defaultProps = {
    handleSubmit: null
};

export default ReviewSingleBinaryJob;
