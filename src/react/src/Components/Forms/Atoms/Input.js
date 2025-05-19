import React from 'react';
import {useField} from 'formik';
import { Form } from 'react-bootstrap';

const Input = ({ title, name, type, help, show=true, ...rest }) => {
    const [field, { error, touched }] = useField(name);
    return <Form.Group controlId={name} className={show ? '' : 'hidden'}>
        <Form.Label>{ title }</Form.Label>
        <Form.Control
            { ...field }
            name={name}
            type={type}
            isValid={touched && !error}
            isInvalid={!!error}
            { ...rest }
        />
        <Form.Text>{help}</Form.Text>
        <Form.Control.Feedback type='invalid' role='alert'>
            {error}
        </Form.Control.Feedback>
    </Form.Group>;
};


export default Input;
