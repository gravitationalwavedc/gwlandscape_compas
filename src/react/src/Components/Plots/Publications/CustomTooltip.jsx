import React from 'react';
import { format } from 'd3-format';
import { Card } from 'react-bootstrap';

const formatValue = (value, zeroValue) => (zeroValue && value < zeroValue ? '0' : format('.6~f')(value));

const CustomTooltip = ({ active, payload, zeroValX, zeroValY }) => {
    if (active && payload && payload.length) {
        return (
            <Card>
                {payload[2] && <div className="font-weight-bold">{`Counts : ${format('.0f')(payload[2].value)}`}</div>}
                <div>{`x: ${formatValue(payload[0].value, zeroValX)}`}</div>
                <div>{`y: ${formatValue(payload[1].value, zeroValY)}`}</div>
            </Card>
        );
    }

    return null;
};

export default CustomTooltip;
