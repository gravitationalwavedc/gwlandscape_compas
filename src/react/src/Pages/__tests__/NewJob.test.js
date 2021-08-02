import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { render, fireEvent, waitFor } from '@testing-library/react';
import NewJob from '../NewJob';
import 'regenerator-runtime/runtime';

/* global router, environment */

describe('new Job Page', () => {

    it('should send a mutation when the form is submitted', async () => {
        expect.hasAssertions();
        const { getByText, getByTestId } = render(<NewJob router={router} />);
        fireEvent.click(getByText('Submit your job'));
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(router.replace).toHaveBeenCalledWith('/compas/job-results/<mock-value-for-field-"jobId">/');
    });

    it('should navigate between tabs', () => {
        expect.hasAssertions();
        const {  getByTestId, getByText } = render(<NewJob />);
        const dataParametersPane = getByTestId('dataParametersPane');
        expect(dataParametersPane).toHaveAttribute('aria-hidden', 'true');
        const signalNavButton = getByText('Atom Parameters');
        fireEvent.click(signalNavButton);
        expect(dataParametersPane).toHaveAttribute('aria-hidden', 'false');
    });
});

