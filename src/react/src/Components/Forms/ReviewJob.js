import React, {useState} from 'react';
import {Button, Col, Row, Table,} from 'react-bootstrap';
import FormCard from './FormCard';

const ReviewJob = ({values, handleSubmit, formik}) => {
    const [errors, setErrors] = useState([]);

    const submitReview = async () => {
        const errors = await formik.validateForm();
        setErrors(Object.values(errors));

        if (Object.keys(errors).length === 0 && errors.constructor === Object) {
            handleSubmit();
        }
    };

    const realData = values.dataChoice === 'real';

    return (
        <React.Fragment>
            <Row>
                <Col>
                    <FormCard title="Source Parameters">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Data type</th>
                                    <td className="text-right">{values.dataChoice}</td>
                                </tr>
                                {realData &&
                                <tr>
                                    <th>Source Dataset</th>
                                    <td className="text-right">{values.sourceDataset}</td>
                                </tr>
                                }
                                <tr>
                                    <th>Start frequency of band (Hz)</th>
                                    <td className="text-right">{values.startFrequencyBand}</td>
                                </tr>
                                <tr>
                                    <th>Minimum Start time (GPS)</th>
                                    <td className="text-right">{values.minStartTime}</td>
                                </tr>
                                <tr>
                                    <th>Maximum Start time (GPS)</th>
                                    <td className="text-right">{values.maxStartTime}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                    <FormCard title="Atom Generation Parameters">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Orbit projected semi-major axis (a sin i, seconds)</th>
                                    <td className="text-right">{values.asini}</td>
                                </tr>
                                <tr>
                                    <th>Time of ascension (GPS s)</th>
                                    <td className="text-right">{values.orbitTp}</td>
                                </tr>
                                <tr>
                                    <th>Frequency search band</th>
                                    <td className="text-right">{values.freqBand}</td>
                                </tr>
                                <tr>
                                    <th>Right ascension (rad)</th>
                                    <td className="text-right">{values.alpha}</td>
                                </tr>
                                <tr>
                                    <th>Declination (rad)</th>
                                    <td className="text-right">{values.delta}</td>
                                </tr>
                                <tr>
                                    <th>Orbital period (s)</th>
                                    <td className="text-right">{values.orbitPeriod}</td>
                                </tr>
                                <tr>
                                    <th>Coherence time (s)</th>
                                    <td className="text-right">{values.driftTime}</td>
                                </tr>
                                <tr>
                                    <th>Frequency step size (Hz)</th>
                                    <td className="text-right">{values.dFreq}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                    <FormCard title="Compas search parameters">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Start time (s)</th>
                                    <td className="text-right">{values.searchStartTime}</td>
                                </tr>
                                <tr>
                                    <th>Duration (s)</th>
                                    <td className="text-right">{values.searchTBlock}</td>
                                </tr>
                                <tr>
                                    <th>Log likelihood threshold</th>
                                    <td className="text-right">{values.searchLLThreshold}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                    <FormCard title="Search a sin i (A0)">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Central_A0</th>
                                    <td className="text-right">{values.searchCentralA0}</td>
                                </tr>
                                <tr>
                                    <th>Band</th>
                                    <td className="text-right">{values.searchA0Band}</td>
                                </tr>
                                <tr>
                                    <th># Bins</th>
                                    <td className="text-right">{values.searchA0Bins}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                    <FormCard title="Search time of ascension (Tp)">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Central_Tp</th>
                                    <td className="text-right">{values.searchCentralOrbitTp}</td>
                                </tr>
                                <tr>
                                    <th>Band</th>
                                    <td className="text-right">{values.searchOrbitTpBand}</td>
                                </tr>
                                <tr>
                                    <th># Bins</th>
                                    <td className="text-right">{values.searchOrbitTpBins}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                    <FormCard title="Search orbital period (P)">
                        <Table>
                            <tbody>
                                <tr>
                                    <th>Central_P</th>
                                    <td className="text-right">{values.searchCentralP}</td>
                                </tr>
                                <tr>
                                    <th>Band</th>
                                    <td className="text-right">{values.searchPBand}</td>
                                </tr>
                                <tr>
                                    <th># Bins</th>
                                    <td className="text-right">{values.searchPBins}</td>
                                </tr>
                            </tbody>
                        </Table>
                    </FormCard>
                </Col>
            </Row>
            {handleSubmit && <Row className="mb-5">
                <Col md={3}>
                    <Button onClick={submitReview}>Submit your job</Button>
                </Col>
                <Col>
                    <ul>{errors.map(value => <li className="text-danger" key={value}>{value}</li>)}</ul>
                </Col>
            </Row>}
        </React.Fragment>
    );
};

ReviewJob.defaultProps = {
    handleSubmit: null
};

export default ReviewJob;
