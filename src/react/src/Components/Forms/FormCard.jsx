import { Card, Col, Row } from 'react-bootstrap';

const FormCard = ({ title, children, disabled, collapsed = false, onTitleClick, ...rest }) => (
    <Card className={disabled ? 'gw-form-card disabled' : 'gw-form-card'} {...rest}>
        <Card.Body>
            <Row>
                <Col>
                    <h3 onClick={onTitleClick}>{title}</h3>
                </Col>
            </Row>
            <Row className={collapsed ? 'hidden' : ''}>
                <Col>{children}</Col>
            </Row>
        </Card.Body>
    </Card>
);

export default FormCard;
