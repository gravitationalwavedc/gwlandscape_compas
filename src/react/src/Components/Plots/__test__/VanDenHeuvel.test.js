import { getEvents } from '../VanDenHeuvelUtils';
import { vdhattr } from '../DataUtil';
import mockData from '../DataMock/graphqlData.json';

describe('van Den Heuvel plot logic', () => {

    it('should return the correct event strings', () => {
        expect.hasAssertions();
        const [imageIndices, sequenceIndices, eventStrings] = getEvents(vdhattr(mockData));
        expect(imageIndices).toStrictEqual([
            2,
            undefined,
            26,
            undefined,
            undefined,
            15,
            undefined,
            undefined,
            49,
            undefined,
            undefined,
            15,
        ]);
        expect(sequenceIndices).toStrictEqual([
            0,
            655,
            729,
            729,
            856,
            938,
            1141,
            1199,
            1572,
            1572,
            1678,
            1688
        ]);
        expect(eventStrings).toStrictEqual([
            'Zero-age main-sequence, metallicity Z=35',
            'Star 1: MS -> HG ',
            'Stable mass transfer from 1 to 2',
            'Star 1: HG -> HeMS ',
            'Star 1: HeMS -> HeHG ',
            'Star 14 undergoes supernova and forms a BH .',
            'Star 2: MS -> HG ',
            'Star 2: HG -> CHeB ',
            'Common envelope initiated by 2',
            'Star 2: CHeB -> HeMS ',
            'Star 2: HeMS -> HeHG ',
            'Star 14 undergoes supernova and forms a BH .'
        ]);
    });
});