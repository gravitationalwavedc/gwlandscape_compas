import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { screen, render, fireEvent, waitFor } from '@testing-library/react';
import NewSingleBinaryJob from '../NewSingleBinaryJob';
import 'regenerator-runtime/runtime';
import userEvent from '@testing-library/user-event';

/* global global */

describe('new single binary job page', () => {
    const mockNewSingleBinaryResult = {
        SingleBinaryJobCreationResult() {
            return {
                jobId: '',
                jsonData: '{}',
                detailedOutputFilePath: '',
            };
        }
    };

    it('should reset parameter values to defaults when use clicks reset form button', async () => {
        expect.hasAssertions();

        render(<NewSingleBinaryJob router={global.router} />);

        const separationInput = screen.getByTestId('separation');
        const orbitalInput = screen.getByTestId('orbitalPeriod');

        fireEvent.change(separationInput, { target: { value: '' } });
        fireEvent.change(orbitalInput, { target: { value: 1.3 } });
        await userEvent.click(screen.getByText('Reset Form'));

        expect(separationInput).toHaveValue(3.5);
        expect(orbitalInput).toHaveValue(null);
    });

    it('should display error message when error is reported from backend', async () => {
        expect.hasAssertions();

        render(<NewSingleBinaryJob router={global.router} />);
        fireEvent.click(screen.getByTestId('submit-btn'));

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());

        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation, mockNewSingleBinaryResult)
        );

        const error = await waitFor(() => screen.getByTestId('error-message'));

        expect(error).toHaveTextContent(/Output file failed to generate and returned an empty string/);
    });
});
