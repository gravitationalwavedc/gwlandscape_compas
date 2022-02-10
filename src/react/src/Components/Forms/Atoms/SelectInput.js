import React from 'react';
import {Form} from 'react-bootstrap';

const SelectInput = ({ title, formik, name, options, show=true, help, ...rest }) =>
    <React.Fragment>
        <Form.Group controlId={name} className={show? '' : 'hidden'}>
            <Form.Label>{ title }</Form.Label>
            <Form.Control
                name= {name}
                as="select"
                custom
                // value={formik.values[name]}
                isValid={formik.touched[name] && !formik.errors[name]}
                isInvalid={!!formik.errors[name]}
                {...formik.getFieldProps(name)} {...rest}>
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
                {formik.errors[name]}
            </Form.Control.Feedback>
        </Form.Group>
    </React.Fragment>;

export default SelectInput;