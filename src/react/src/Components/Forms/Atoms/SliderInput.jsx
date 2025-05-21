import React from 'react';
import { Form } from 'react-bootstrap';
import { useField } from 'formik';

const SliderInput = ({ title, name, text, ...rest }) => {
    const [field] = useField(name);

    return (
        <Form.Group>
            <Form.Label>{title}</Form.Label>
            <Form.Control {...field} type="range" className="mb-0" {...rest} />
            <Form.Text>{text}</Form.Text>
        </Form.Group>
    );
};

export default SliderInput;
