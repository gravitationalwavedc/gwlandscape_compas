import {formatAxis, logString, getTickMarks} from '../Utils';

describe('formatAxis', () => {
    it('formats floats above and below 1000 correctly', () => {
        expect.hasAssertions();
        expect(formatAxis(9)).toBe('9');
        expect(formatAxis(9.90)).toBe('9.9');
        expect(formatAxis(9.99)).toBe('9.99');
        expect(formatAxis(9.991)).toBe('9.99');
        expect(formatAxis(99)).toBe('99');
        expect(formatAxis(999)).toBe('999');
        expect(formatAxis(1000)).toBe('1.0e+3');
        expect(formatAxis(10500)).toBe('1.1e+4');
    });
});

describe('logString', () => {
    it('formats string with log[] if desired', () => {
        expect.hasAssertions();
        expect(logString('test')).toBe('log[test]');
        expect(logString('test', false)).toBe('test');
    });
});

describe('getTickMarks', () => {
    it('creates the correct array', () => {
        expect.hasAssertions();
        expect(getTickMarks(0, 10, 10)).toStrictEqual([0,1,2,3,4,5,6,7,8,9,10]);
        expect(getTickMarks(0, 10, 5)).toStrictEqual([0,2.5,5,7.5,10]);
        expect(getTickMarks(0, 10, 3)).toStrictEqual([0,5,10]);
        expect(getTickMarks(110, 250, 5)).toStrictEqual([100,125,150,175,200,225,250]);
        expect(getTickMarks(110, 250, 3)).toStrictEqual([100,150,200,250]);
        expect(getTickMarks(1703, 50150, 5)).toStrictEqual([0,10000,20000,30000,40000,50000,60000]);
        expect(getTickMarks(1703, 50150, 3)).toStrictEqual([0,20000,40000,60000]);
    });
});