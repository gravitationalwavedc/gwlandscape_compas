import { format } from 'd3-format';

const ExponentTick = ({ x, y, payload, orientation }) => (
    <g className="exponent-tick" transform={`translate(${x},${y})`}>
        <text
            x={0}
            y={0}
            dy={orientation === 'bottom' ? 16 : 0}
            dx={orientation === 'bottom' ? 0 : -16}
            textAnchor="middle"
        >
            10
            <tspan dy={-6}>{format('.2~f')(Math.log10(payload.value))}</tspan>
        </text>
    </g>
);

export default ExponentTick;
