import React from 'react';
import { render, screen } from '@testing-library/react';
import PublicationCard from '../PublicationCard';

describe('publications Page', () => {
    const publication = {
        author: 'Buffy Summers',
        title: 'Vampire Slaying: A Retrospective',
        year: 2003,
        keywords: {
            edges: [
                {
                    node: {tag: 'Keyword1'}
                },
                {
                    node: {tag: 'Keyword2'}
                },
            ]
        }
    };

    it('renders', async () => {
        expect.hasAssertions();
        render(<PublicationCard publication={publication} />);
        expect(screen.getByText(publication.title)).toBeInTheDocument();
        expect(screen.getByText(`${publication.author} - ${publication.year}`)).toBeInTheDocument();
        expect(screen.getByText(
            `${publication.keywords.edges[0].node.tag}, ${publication.keywords.edges[1].node.tag}`
        )).toBeInTheDocument();
    });
});
