import React from 'react';
import { render, screen } from '@testing-library/react';
import PublicationCard from '../PublicationCard';

/* global router */

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
        },
        datasetModels: {
            edges: [
                {
                    node: {id: 'test-id'}
                }
            ]
        }
    };

    it('renders', async () => {
        expect.hasAssertions();
        render(<PublicationCard publication={publication} match={{}} router={router} />);
        expect(screen.getByText(publication.title)).toBeInTheDocument();
        expect(screen.getByText(`${publication.author} · ${publication.year}`)).toBeInTheDocument();
        expect(screen.getByText(
            `${publication.keywords.edges[0].node.tag}, ${publication.keywords.edges[1].node.tag}`
        )).toBeInTheDocument();
    });
});
