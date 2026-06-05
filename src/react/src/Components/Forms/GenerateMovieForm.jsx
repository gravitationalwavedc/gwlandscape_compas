import { Col, Row } from 'react-bootstrap';
import SelectInput from './Atoms/SelectInput';

const GenerateMovieForm = () => (
    <Row>
        <Col>
            <SelectInput
                title="Scaling"
                name="scaling"
                type="string"
                options={[
                    { value: 'log', label: 'Log' },
                    { value: 'linear', label: 'Linear' },
                ]}
                help="Select log or linear scaling"
                validate={false}
            />
        </Col>
        <Col>
            <SelectInput
                title="Images"
                name="images"
                type="string"
                options={[
                    { value: 'default', label: 'Default' },
                    { value: 'tulips', label: 'Tulips' },
                ]}
                help="Default renders images, Tulips renders perceived colour based on temperature"
                validate={false}
            />
        </Col>
    </Row>
);

export default GenerateMovieForm;
