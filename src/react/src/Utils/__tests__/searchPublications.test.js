import searchPublications from '../searchPublications';

describe('searchPublications', () => {
    const keywordsToConnection = (keywords) => ({
        edges: keywords.map(keyword => ({node: {tag: keyword}}))
    });

    const arrayFromIndices = (array, indices) => indices.map(i => array[i]);

    const publications = [
        {
            author: 'Buffy Summers',
            title: 'A Publication',
            year: 1997,
            keywords: keywordsToConnection(['Keyword'])
        },
        {
            author: 'Buffy Summers',
            title: 'Vampire Slaying: A Retrospective',
            year: 2003,
            keywords: keywordsToConnection(['Science', 'Garlic'])
        },
        {
            author: 'Bill Nye',
            title: 'A Journal Article',
            year: 1993,
            keywords: keywordsToConnection(['Science', 'Guy'])
        },
        {
            author: 'Bill Nye',
            title: 'The Dark Side of Science Education',
            year: 1999,
            keywords: keywordsToConnection(['Space'])
        },
        {
            author: 'James Webb',
            title: 'A Thesis',
            year: 2003,
            keywords: keywordsToConnection(['Space', 'Telescope'])
        },
        {
            author: 'James Webb',
            title: 'Hexagonal Mirrors: How Bees Are Really the Root of Everything',
            year: 2022,
            keywords: keywordsToConnection(['Down With Hubble'])
        },
    ];

    it('will filter publications based on author name', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, 'buffy');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0,1]));
        filtered = searchPublications(publications, 'NYE');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [2,3]));
        filtered = searchPublications(publications, 'James');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [4,5]));
    });

    it('will filter publications based on title', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, 'Publication');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0]));
        filtered = searchPublications(publications, 'Journal');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [2]));
        filtered = searchPublications(publications, 'THESIS');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [4]));
    });

    it('will filter publications based on year', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, '1997');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0]));
        filtered = searchPublications(publications, '1993');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [2]));
        filtered = searchPublications(publications, '2022');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [5]));
    });

    it('will filter publications based on keyword', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, 'Keyword');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0]));
        filtered = searchPublications(publications, 'GUY');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [2]));
        filtered = searchPublications(publications, 'telescope');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [4]));
    });

    it('will filter publications based on incomplete terms', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, 'buff');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0,1]));
        filtered = searchPublications(publications, '19');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [0,2,3]));
        filtered = searchPublications(publications, 'tele');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [4]));
    });

    it('will filter publications based on multiple terms', () => {
        expect.hasAssertions();
        let filtered = searchPublications(publications, 'science bill');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [2,3]));
        filtered = searchPublications(publications, '2003 telescope');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [4]));
        filtered = searchPublications(publications, '20 vampire');
        expect(filtered).toStrictEqual(arrayFromIndices(publications, [1]));
    });
});
