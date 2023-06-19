import React from 'react';
import { Form } from 'react-bootstrap';

const SelectInput = ({ title, value, options, ...rest }) =>
    <Form.Group>
        <Form.Label>{ title }</Form.Label>
        <Form.Control
            as="select"
            custom
            value={value}
            {...rest}
        >
            {options.map(({label, value}) =>
                <option
                    value={value}
                    id={label}
                    key={label}>
                    {label}
                </option>
            )}
        </Form.Control>
    </Form.Group>;

const SliderInput = ({ title, text, value, ...rest }) => 
    <Form.Group>
        <Form.Label>{title}</Form.Label>
        <Form.Control
            type="range"
            className="mb-0"
            value={value}
            {...rest}
        />
        <Form.Text>{text}</Form.Text>
    </Form.Group>;

export { SelectInput, SliderInput };