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
            edges: []
        }
    };
    const datasetModels = {
        edges: [
            {
                node: {id: 'test-id'}
            }
        ]
    };

    it('renders', async () => {
        expect.hasAssertions();
        render(<PublicationCard publication={publication} match={{}} router={router} />);
        expect(screen.getByText(publication.title)).toBeInTheDocument();
        expect(screen.getByText(`${publication.author} · ${publication.year}`)).toBeInTheDocument();
        expect(screen.getByText(
            `${publication.keywords.edges[0].node.tag}, ${publication.keywords.edges[1].node.tag}`
        )).toBeInTheDocument();
        expect(screen.getByText('No available models')).toBeInTheDocument();
    });

    it('has an active button when supplied with datasets', async () => {
        expect.hasAssertions();
        publication.datasetModels = datasetModels;
        render(<PublicationCard publication={publication} match={{}} router={router} />);
        expect(screen.getByText('Start interactive visualisation')).toBeInTheDocument();
    });
});
