import { Col, Row } from 'react-bootstrap';
import Input from './Atoms/Input';

const BasicParametersForm = () => (
    <>
        <Row>
            <Col>
                <Input
                    title="Mass 1 (M&#9737;)"
                    name="mass1"
                    type="number"
                    help="Mass of the initially more massive star.  0 < Value < 150"
                />
            </Col>
            <Col>
                <Input
                    title="Mass 2 (M&#9737;)"
                    name="mass2"
                    type="number"
                    help="Mass of the initially less massive star. 0 < Value < 150"
                />
            </Col>
        </Row>
        <Row>
            <Col>
                <Input
                    title="Metallicity (Z)"
                    name="metallicity"
                    type="number"
                    help="Metallicity of stars.  1E-4 < Value < 0.03"
                />
                <Input
                    title="Eccentricity"
                    name="eccentricity"
                    type="number"
                    help="Orbital eccentricity of the binary. 0 <= Value < 1"
                />
                <Input
                    title="Separation (AU)"
                    name="separation"
                    data-testid="separation"
                    type="number"
                    help="Value > 0. Only used with no Orbital Period"
                />
                <Input
                    title="Orbital Period (days)"
                    name="orbitalPeriod"
                    data-testid="orbitalPeriod"
                    type="number"
                    help="Value > 0. Only used with no Separation"
                />
            </Col>
            <Col />
        </Row>
    </>
);

export default BasicParametersForm;
