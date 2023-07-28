import React from 'react';
import {Form} from 'react-bootstrap';
import {useField} from 'formik';

const SelectInput = ({ title, name, options, show=true, help, validate=true, ...rest }) => {
    const [field, { error, touched }] = useField(name);
    const validProps = validate ? {isValid: touched && !error, isInvalid: !!error} : {};
    return <Form.Group controlId={name} className={show ? '' : 'hidden'}>
        <Form.Label>{title}</Form.Label>
        <Form.Control
            { ...field }
            as="select"
            custom
            { ...validProps }
            { ...rest }
        >
            {options.map(({label, value}) =>
                <option
                    value={value}
                    id={name + label}
                    key={name + label}>
                    {label}
                </option>
            )}
        </Form.Control>
        <Form.Text>{help}</Form.Text>
        <Form.Control.Feedback type='invalid'>
            {error}
        </Form.Control.Feedback>
    </Form.Group>;
};

export default SelectInput;