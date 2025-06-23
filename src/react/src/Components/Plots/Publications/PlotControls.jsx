import { useFormikContext } from 'formik';

import { Col, Button } from 'react-bootstrap';
import SelectInput from '../../Forms/Atoms/SelectInput';
import SliderInput from '../../Forms/Atoms/SliderInput';

const toOptions = (labels) => labels.map((label) => ({ value: label, label: label }));

const PlotControls = ({ relay, groups, subgroups, colourMaps }) => {
    const { values, setFieldValue } = useFormikContext();
    const groupOptions = toOptions(groups);
    const subgroupOptions = toOptions(subgroups);
    const colourMapOptions = toOptions(colourMaps);

    return (
        <Col md={4}>
            <h5>Visualisation</h5>
            <SelectInput
                data-testid="group"
                title="Group"
                name="group"
                options={groupOptions}
                onChange={(e) => {
                    // setFieldValue('group', e.target.value);
                    relay.refetch({ rootGroup: e.target.value });
                }}
                validate={false}
            />
            <SelectInput
                data-testid="x-axis"
                title="X-axis"
                name="subgroupX"
                options={subgroupOptions}
                onChange={(e) => {
                    // setFieldValue('subgroupX', e.target.value);
                    relay.refetch({
                        rootGroup: values.group,
                        subgroupY: values.subgroupY,
                        subgroupX: e.target.value,
                    });
                }}
                validate={false}
            />
            <SelectInput
                data-testid="y-axis"
                title="Y-axis"
                name="subgroupY"
                options={subgroupOptions}
                onChange={(e) => {
                    // setFieldValue('subgroupY', e.target.value);
                    relay.refetch({
                        rootGroup: values.group,
                        subgroupX: values.subgroupX,
                        subgroupY: e.target.value,
                    });
                }}
                validate={false}
            />
            <SelectInput title="Colour Bar" name="colourMap" options={colourMapOptions} validate={false} />
            <SliderInput
                title={`Stride interval: ${values.strideLength}`}
                name="strideLength"
                text={
                    values.strideLength > 1
                        ? `Showing ${Math.ceil(values.totalLength / values.strideLength)} of ${values.totalLength} points`
                        : `Showing the whole dataset of ${values.totalLength} points`
                }
                min={1}
                max={20}
                onMouseUp={(e) => {
                    setFieldValue('strideLength', e.target.value);
                    relay.refetch({
                        rootGroup: values.group,
                        subgroupX: values.subgroupX,
                        subgroupY: values.subgroupY,
                        strideLength: e.target.value,
                    });
                }}
            />
            <Button
                variant="outline-primary"
                onClick={() =>
                    relay.refetch({
                        rootGroup: null,
                    })
                }
            >
                Reset Visualisation
            </Button>
        </Col>
    );
};

export default PlotControls;
