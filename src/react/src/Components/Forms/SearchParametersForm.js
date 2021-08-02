import React from 'react';
import { Button, Col, Row } from 'react-bootstrap';
import Input from './Atoms/Input';
import FormCard from './FormCard';

const SearchParametersForm = ({formik, handlePageChange}) =>
    <Row>
        <Col>
            <FormCard title="Compas Search Parameters">
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Start time (s)"
                            name="searchStartTime"
                            type="number"/>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Duration (s)"
                            name="searchTBlock"
                            type="number"/>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Log likelihood threshold"
                            name="searchLLThreshold"
                            type="number"/>
                    </Col>
                </Row>
            </FormCard>
            <FormCard title="Search a sin i">
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Central_A0"
                            name="searchCentralA0"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="Band"
                            name="searchA0Band"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="# Bins"
                            name="searchA0Bins"
                            type="number"/>
                    </Col>
                </Row>
            </FormCard>
            <FormCard title="Search time of ascension">
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Central_Tp"
                            name="searchCentralOrbitTp"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="Band"
                            name="searchOrbitTpBand"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="# Bins"
                            name="searchOrbitTpBins"
                            type="number"/>
                    </Col>
                </Row>
            </FormCard>
            <FormCard title="Search orbital period">
                <Row>
                    <Col>
                        <Input
                            formik={formik}
                            title="Central_P"
                            name="searchCentralP"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="Band"
                            name="searchPBand"
                            type="number"/>
                    </Col>
                    <Col>
                        <Input
                            formik={formik}
                            title="# Bins"
                            name="searchPBins"
                            type="number"/>
                    </Col>
                </Row>
            </FormCard>
            <Row>
                <Col>
                    <Button onClick={() => handlePageChange('review')}>Save and continue</Button>
                </Col>
            </Row>
        </Col>
    </Row>
;

export default SearchParametersForm;
