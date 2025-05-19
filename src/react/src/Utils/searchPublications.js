const filterPublications = (publications, term) => publications.filter(
    p => (
        p.author.toLowerCase().includes(term) ||
        p.title.toLowerCase().includes(term) ||
        p.keywords.edges.some(({node}) => node.tag.toLowerCase().includes(term)) ||
        String(p.year).includes(term)
    )
);

const searchPublications = (publications, search) => {
    const terms = search.toLowerCase().split(' ');
    return terms.reduce(
        (filteredPubs, term) => filterPublications(filteredPubs, term),
        publications
    );
};

export default searchPublications;