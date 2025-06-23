import React from 'react';
import { render, screen } from '@testing-library/react';
import PublicationList from '../PublicationList';

/* global router */

describe('publications Page', () => {
    const publications = [
        {
            id: '1',
            author: 'Buffy Summers',
            title: 'Vampire Slaying: A Retrospective',
            year: 2003,
            keywords: {
                edges: [
                    {
                        node: { tag: 'Keyword1' },
                    },
                ],
            },
            datasetModels: {
                edges: [
                    {
                        node: { id: 'test-id' },
                    },
                ],
            },
        },
        {
            id: '2',
            author: 'Bill Nye',
            title: 'A Journal Article',
            year: 1993,
            keywords: {
                edges: [
                    {
                        node: { tag: 'Keyword2' },
                    },
                ],
            },
            datasetModels: {
                edges: [
                    {
                        node: { id: 'test-id' },
                    },
                ],
            },
        },
    ];

    it('renders', async () => {
        expect.hasAssertions();
        render(<PublicationList publications={publications} match={{}} router={router} />);
        expect(screen.getByText(publications[0].title)).toBeInTheDocument();
        expect(screen.getByText(publications[1].title)).toBeInTheDocument();
    });
    it('renders message if no publications', async () => {
        expect.hasAssertions();
        render(<PublicationList publications={[]} />);
        expect(screen.getByText('No publications have been uploaded.')).toBeInTheDocument();
    });
});
