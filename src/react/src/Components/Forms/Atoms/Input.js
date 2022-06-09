import React from 'react';
import { Form } from 'react-bootstrap';

const Input = ({formik, title, name, type, help, show= true, ...rest}) =>
    <Form.Group controlId={ name } className={show? '' : 'hidden'}>
        <Form.Label>{ title }</Form.Label>
        <Form.Control 
            name={ name }
            type={ type } 
            isValid={formik.touched[name] && !formik.errors[name]}
            isInvalid={!!formik.errors[name]}
            {...formik.getFieldProps(name)} {...rest}/>
        <Form.Text>{help}</Form.Text>
        {formik.errors[name] &&
            <Form.Control.Feedback type='invalid' role='alert'>
                {formik.errors[name]}
            </Form.Control.Feedback>
        }
    </Form.Group>;


export default Input;
