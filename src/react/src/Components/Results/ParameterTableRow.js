import React from 'react';
import {Row, Col} from 'react-bootstrap';

const ParameterTableRow = ({params}) => <Row>
    <Col md={4}>{params[0].name}</Col>
    <Col md={2}>{params[0].value}</Col>
    <Col md={4}>{params[1].name}</Col>
    <Col md={2}>{params[1].value}</Col>
</Row>;

export default ParameterTableRow;