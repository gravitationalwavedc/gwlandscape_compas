import {filterGroupDataByDomain} from '../Utils';

const meta = [
    {'xKey': 'x', 'yKey': 'y0'},
    {'xKey': 'x', 'yKey': 'y1'},
];

const group = {
    meta,
    data: [
        {x: 0, y0: 10, y1: 100},
        {x: 1, y0: 11, y1: 110},
        {x: 2, y0: 12, y1: 120},
        {x: 3, y0: 13, y1: 130},
        {x: 4, y0: 14, y1: 140},
        {x: 5, y0: 15, y1: 150},
        {x: 6, y0: 16, y1: 160},
    ]
};

describe('filterGroupDataByDomain', () => {
    it('will filter no data if domain surrounds everything', () => {
        expect.hasAssertions();
        const filteredGroup = filterGroupDataByDomain(group, {x1: 0, x2: 6, y1: 0, y2: 200});
        expect(filteredGroup).toStrictEqual({meta, data: [
            {x: 0, y0: 10, y1: 100},
            {x: 1, y0: 11, y1: 110},
            {x: 2, y0: 12, y1: 120},
            {x: 3, y0: 13, y1: 130},
            {x: 4, y0: 14, y1: 140},
            {x: 5, y0: 15, y1: 150},
            {x: 6, y0: 16, y1: 160},
        ]});
    });

    it('will filter data within x domain, including the next points outside domain', () => {
        expect.hasAssertions();
        const filteredGroup = filterGroupDataByDomain(group, {x1: 2, x2: 4, y1: 0, y2: 200});
        expect(filteredGroup).toStrictEqual({meta, data: [
            {x: 1, y0: 11, y1: 110},
            {x: 2, y0: 12, y1: 120},
            {x: 3, y0: 13, y1: 130},
            {x: 4, y0: 14, y1: 140},
            {x: 5, y0: 15, y1: 150},
        ]});
    });

    it('will filter data within y domain, including the next points outside domain', () => {
        expect.hasAssertions();
        const filteredGroup1 = filterGroupDataByDomain(group, {x1: 0, x2: 6, y1: 12, y2: 14});
        expect(filteredGroup1).toStrictEqual({meta, data: [
            {x: 1, y0: 11, y1: 110},
            {x: 2, y0: 12, y1: 120},
            {x: 3, y0: 13, y1: 130},
            {x: 4, y0: 14, y1: 140},
            {x: 5, y0: 15, y1: 150},
        ]});
        const filteredGroup2 = filterGroupDataByDomain(group, {x1: 0, x2: 6, y1: 13, y2: 130});
        expect(filteredGroup2).toStrictEqual({meta, data: [
            {x: 0, y0: 10, y1: 100},
            {x: 1, y0: 11, y1: 110},
            {x: 2, y0: 12, y1: 120},
            {x: 3, y0: 13, y1: 130},
            {x: 4, y0: 14, y1: 140},
            {x: 5, y0: 15, y1: 150},
            {x: 6, y0: 16, y1: 160},
        ]});
    });
});
