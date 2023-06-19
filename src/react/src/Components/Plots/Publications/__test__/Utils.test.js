import {formatAxis, logString, createTicks} from '../Utils';

describe('formatAxis', () => {
    it('formats floats above and below 1000 correctly', () => {
        expect.hasAssertions();
        expect(formatAxis(9)).toBe('9.0');
        expect(formatAxis(9.99)).toBe('10.0');
        expect(formatAxis(99)).toBe('99.0');
        expect(formatAxis(999)).toBe('999.0');
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

describe('createTicks', () => {
    it('creates the correct array', () => {
        expect.hasAssertions();
        expect(createTicks(0, 10, 10)).toStrictEqual([0,1,2,3,4,5,6,7,8,9,10]);
        expect(createTicks(0, 10, 5)).toStrictEqual([0,2,4,6,8,10]);
    });
});