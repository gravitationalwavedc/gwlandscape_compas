import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {fireEvent, render, waitFor} from '@testing-library/react';
import NewJob from '../NewJob';
import 'regenerator-runtime';

/* global global */

describe('new compas population job page', () => {
    it('should send a mutation when the form is submitted', async () => {
        expect.hasAssertions();
        jest.spyOn(console, 'log').mockImplementation();
        const {getAllByText} = render(<NewJob router={global.router}/>);
        fireEvent.click(getAllByText('Submit your job')[0]);
        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(console.log).toHaveBeenCalledWith('<mock-value-for-field-"jobId">');
    });
});