import React from 'react';
import {Col, Row} from 'react-bootstrap';
import FormCard from './FormCard';
import Input from './Atoms/Input';

const KickParametersForm = ({formik, collapsed, onTitleClick}) => (
    <React.Fragment>
        <h3>Kick Parameters</h3>
        <Row>
            <Col>
                <Input
                    formik={formik}
                    title="Velocity Random Number 1"
                    name="velocityRandomNumber1"
                    type="number"
                    help="Value to be used to draw the kick magnitude for the primary star of a binary
                                    system when evolving in BSE mode, should the star undergo a supernova event,
                                    0 < Value < 1"
                />
                <Input
                    formik={formik}
                    title="Velocity 1 (km/s)"
                    name="velocity1"
                    type="number"
                    help="Value to be used as the (drawn) kick magnitude for the primary star of a
                                    binary system when evolving in BSE mode, should the star undergo a supernova event
                                    (km s −1 ), Value > 0"
                />
                <Input
                    formik={formik}
                    title="Theta 1"
                    name="theta1"
                    type="number"
                    data-testid="theta1"
                    help="The angle between the orbital plane and the ’z’ axis of the supernova vector
                                    for the for the primary star of a binary system when evolving in BSE mode, should
                                    it undergo a supernova event (radians), 0 < Value < 2pi"
                />
                <Input
                    formik={formik}
                    title="Phi 1"
                    name="phi1"
                    type="number"
                    data-testid="phi1"
                    help="The angle between ’x’ and ’y’, both in the orbital plane of the supernova
                                    vector, for the for the primary star of a binary system when evolving in BSE mode,
                                    should it undergo a supernova event (radians), 0 < Value < 2pi"
                />
                <Input
                    formik={formik}
                    title="Mean Anomaly 1"
                    name="meanAnomaly1"
                    type="number"
                    help="The mean anomaly at the instant of the supernova for the primary star of a
                                    binary system when evolving in BSE mode, should it undergo a supernova event,
                                    0 < Value < 2pi"
                />
            </Col>
            <Col>
                <Input
                    formik={formik}
                    title="Velocity Random Number 2"
                    name="velocityRandomNumber2"
                    type="number"
                    help="Value to be used to draw the kick magnitude for the second star of a binary
                                    system when evolving in BSE mode, should the star undergo a supernova event,
                                    0 < Value < 1"
                />
                <Input
                    formik={formik}
                    title="Velocity 2 (km/s)"
                    name="velocity2"
                    type="number"
                    help="Value to be used as the (drawn) kick magnitude for the second star of a
                                    binary system when evolving in BSE mode, should the star undergo a supernova event
                                    (km s −1 ), Value > 0"
                />
                <Input
                    formik={formik}
                    title="Theta 2"
                    name="theta2"
                    type="number"
                    data-testid="theta2"
                    help="The angle between the orbital plane and the ’z’ axis of the supernova vector
                                    for the for the second star of a binary system when evolving in BSE mode,
                                    should it undergo a supernova event (radians), 0 < Value < 2pi"
                />
                <Input
                    formik={formik}
                    title="Phi 2"
                    name="phi2"
                    type="number"
                    data-testid="phi2"
                    help="The angle between ’x’ and ’y’, both in the orbital plane of the supernova
                                    vector, for the for the secondary star of a binary system when evolving in BSE
                                    mode, should it undergo a supernova event (radians), 0 < Value < 2pi"
                />
                <Input
                    formik={formik}
                    title="Mean Anomaly 2"
                    name="meanAnomaly2"
                    type="number"
                    help="The mean anomaly at the instant of the supernova for the secondary star of
                                    a binary system when evolving in BSE mode, should it undergo a supernova event,
                                    0 < Value < 2pi"
                />
            </Col>
        </Row>
    </React.Fragment>
);

export default KickParametersForm;
