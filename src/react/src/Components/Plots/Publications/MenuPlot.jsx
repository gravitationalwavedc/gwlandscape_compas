import { useRef } from 'react';
import { graphql, createRefetchContainer } from 'react-relay';
import { Formik } from 'formik';

import DatasetPlot from './DatasetPlot';
import { Col, Row } from 'react-bootstrap';
import PlotControls from './PlotControls';

const colourMaps = ['viridis', 'cividis', 'magma', 'inferno', 'spectral'];

const MenuPlot = ({ data, relay }) => {
    const plotMeta = data?.plotMeta;
    const plotData = data?.plotData;

    const { groups, subgroups, subgroupXUnit, subgroupYUnit, ...restMeta } = plotMeta || {};
    const { histData, scatterData, ...restData } = plotData || {};

    const formikRef = useRef();

    return plotMeta ? (
        <Formik
            innerRef={(f) => (formikRef.current = f)}
            initialValues={{ ...restMeta, colourMap: formikRef?.current?.values.colourMap || colourMaps[0] }}
            validateOnChange={false}
            validateOnBlur={false}
            enableReinitialize={!!plotMeta}
        >
            {({ values }) => (
                <Row>
                    <PlotControls relay={relay} groups={groups} subgroups={subgroups} colourMaps={colourMaps} />
                    <Col md={8}>
                        {plotData ? (
                            <DatasetPlot
                                histData={JSON.parse(histData)}
                                scatterData={JSON.parse(scatterData)}
                                axis={[
                                    `${values.subgroupX}${subgroupXUnit ? ` / ${subgroupXUnit}` : ''}`,
                                    `${values.subgroupY}${subgroupYUnit ? ` / ${subgroupYUnit}` : ''}`,
                                ]}
                                colourMap={values.colourMap}
                                {...restData}
                            />
                        ) : (
                            <div>This data cannot be plotted</div>
                        )}
                    </Col>
                </Row>
            )}
        </Formik>
    ) : (
        <div>The dataset was unable to be read</div>
    );
};

export default createRefetchContainer(
    MenuPlot,
    {
        data: graphql`
            fragment MenuPlot_data on CompasDatasetModelNode
            @argumentDefinitions(
                rootGroup: { type: "String" }
                subgroupX: { type: "String" }
                subgroupY: { type: "String" }
                strideLength: { type: "Int" }
            ) {
                plotMeta(
                    rootGroup: $rootGroup
                    subgroupX: $subgroupX
                    subgroupY: $subgroupY
                    strideLength: $strideLength
                ) {
                    groups
                    group
                    subgroups
                    subgroupX
                    subgroupY
                    subgroupXUnit
                    subgroupYUnit
                    strideLength
                    totalLength
                }
                plotData(
                    rootGroup: $rootGroup
                    subgroupX: $subgroupX
                    subgroupY: $subgroupY
                    strideLength: $strideLength
                ) {
                    histData
                    sides
                    scatterData
                    minMaxX
                    minMaxY
                    nullCheckX
                    nullCheckY
                    logCheckX
                    logCheckY
                    boolCheckX
                    boolCheckY
                }
            }
        `,
    },
    graphql`
        query MenuPlotRefetchQuery(
            $publicationId: ID!
            $datasetId: ID
            $rootGroup: String
            $subgroupX: String
            $subgroupY: String
            $strideLength: Int
        ) {
            compasPublication(id: $publicationId) {
                datasetModels(first: 1, id: $datasetId) {
                    edges {
                        node {
                            ...MenuPlot_data
                                @arguments(
                                    rootGroup: $rootGroup
                                    subgroupX: $subgroupX
                                    subgroupY: $subgroupY
                                    strideLength: $strideLength
                                )
                        }
                    }
                }
            }
        }
    `,
);
