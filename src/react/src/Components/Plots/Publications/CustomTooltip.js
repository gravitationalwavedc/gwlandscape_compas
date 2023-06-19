import React from 'react';
import { format } from 'd3-format';
import { Card } from 'react-bootstrap';

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return <Card>
            {
                payload[2] && <div className='font-weight-bold'>
                    {`Counts : ${format('.0f')(payload[2].value)}`}
                </div>
            }
            <div>{`${format('.4f')(payload[0].value)}, ${format('.4f')(payload[1].value)}`}</div>
        </Card>;
    }

    return null;
};

export default CustomTooltip;