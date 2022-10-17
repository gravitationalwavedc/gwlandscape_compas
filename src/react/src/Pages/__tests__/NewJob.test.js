import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {fireEvent, render, waitFor} from '@testing-library/react';
import NewJob from '../NewJob';
import 'regenerator-runtime';

/* global router,environment */

describe('new compas population job page', () => {
    it('should send a mutation when the form is submitted', async () => {
        expect.hasAssertions();
        const {getAllByText} = render(<NewJob router={router}/>);
        fireEvent.click(getAllByText('Submit your job')[0]);
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(router.replace).toHaveBeenCalledWith('/compas/job-results/<mock-value-for-field-"jobId">/');
    });
});