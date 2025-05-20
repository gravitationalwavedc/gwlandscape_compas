import React, {useState} from 'react';
import {Button, Col, Row} from 'react-bootstrap';
import {useFormikContext} from 'formik';

const ReviewJob = ({ disableButtons }) => {
    const [errors, setErrors] = useState([]);
    
    const {handleSubmit, handleReset, validateForm} = useFormikContext();
    
    const submitReview = async () => {
        const errors = await validateForm();
        setErrors(Object.values(errors));

        if (Object.keys(errors).length === 0 && errors.constructor === Object) {
            handleSubmit();
        }
    };

    return (
        <React.Fragment>
            {handleSubmit && <Row>
                <Col>
                    <Button
                        data-testid="submit-btn"
                        onClick={submitReview}
                        disabled={disableButtons}
                        className="mr-3"
                    >Start Simulation</Button>
                    <Button
                        data-testid="reset-btn"
                        disabled={disableButtons}
                        onClick={handleReset}>Reset Form</Button>
                    <ul>{errors.map(value => <li className="text-danger" key={value}>{value}</li>)}</ul>
                </Col>
            </Row>}
        </React.Fragment>
    );
};

ReviewJob.defaultProps = {
    handleSubmit: null
};

export default ReviewJob;
