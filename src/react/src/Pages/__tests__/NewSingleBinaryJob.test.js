import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { screen, render, fireEvent, waitFor } from '@testing-library/react';
import NewSingleBinaryJob from '../NewSingleBinaryJob';
import 'regenerator-runtime/runtime';
import userEvent from '@testing-library/user-event';

/* global global */


describe('new single binary job page', () => {
    it('should reset parameter values to defaults when use clicks reset form button', async () => {
        expect.hasAssertions();

        jest.spyOn(global, 'scrollTo').mockImplementation();

        render(<NewSingleBinaryJob router={global.router}/>);
        //Clear Separation and add value for OrbitalPeriod to make sure form submits if an input was cleared
        const separationInput = screen.getByTestId('separation');
        const orbitalInput = screen.getByTestId('orbitalPeriod');

        fireEvent.change(separationInput, {target: {value: ''}});
        fireEvent.change(orbitalInput, {target: {value: 1.3}});

        await waitFor(() => userEvent.click(screen.getByText('Reset Form')));
        expect(separationInput).toHaveValue(1.02);
        expect(orbitalInput).toHaveValue(null);
    });

    it('checks if output files are generated when user clicks submit', async () => {
        expect.hasAssertions();

        jest.spyOn(global, 'scrollTo').mockImplementation();

        render(<NewSingleBinaryJob router={global.router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());

        global.environment.mock.resolve(operation, MockPayloadGenerator.generate(operation));

        expect(screen.getByTestId('download-link')).toBeTruthy();
    });

    const mockNewSingleBinaryResult = {
        SingleBinaryJobCreationResult() {
            return {
                jobId: '',
                jsonData: '',
                detailedOutputFilePath: ''
            };
        }
    };

    it('should display error message when error is reported from backend', async () => {
        expect.hasAssertions();

        render(<NewSingleBinaryJob router={global.router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());

        // check submit & reset buttons are disable while job is running
        expect(screen.getByTestId('submit-btn')).toBeDisabled();
        expect(screen.getByTestId('reset-btn')).toBeDisabled();

        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation, mockNewSingleBinaryResult)
        );

        expect(screen.getByTestId('error-msg')).toHaveTextContent('Output could not be generated');

        // check submit & reset buttons are enabled again after job returns error
        expect(screen.getByTestId('submit-btn')).not.toBeDisabled();
        expect(screen.getByTestId('reset-btn')).not.toBeDisabled();

    });

    it('should generate output files when user clicks submit ' +
        'and reset all files when user clicks submit again', async () => {
        expect.hasAssertions();

        // jest.useFakeTimers();
        jest.spyOn(global, 'scrollTo').mockImplementation();

        render(<NewSingleBinaryJob router={global.router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());

        // check submit & reset buttons are disabled after submitting the job
        expect(screen.getByTestId('submit-btn')).toBeDisabled();
        expect(screen.getByTestId('reset-btn')).toBeDisabled();

        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );

        expect(screen.getByTestId('download-link')).toHaveProperty('href', 'https://gwlandscape.org.au<mock-value-for-field-"detailedOutputFilePath">');

        // check submit & reset buttons are enabled again after job succeeds and plots are generated
        expect(screen.getByTestId('submit-btn')).not.toBeDisabled();
        expect(screen.getByTestId('reset-btn')).not.toBeDisabled();

        //Clear Separation and add value for OrbitalPeriod to make sure form submits if an input was cleared
        const separationInput = screen.getByLabelText('Separation (AU)');
        const orbitalInput = screen.getByLabelText('Orbital Period (days)');
        fireEvent.change(separationInput, {target: {value:''}});
        fireEvent.change(orbitalInput, {target: {value:1.3}});
        await waitFor(() => userEvent.click(screen.getByTestId('submit-btn')));

        const operation1 = await waitFor(() => global.environment.mock.getMostRecentOperation());
        global.environment.mock.resolve(operation1, MockPayloadGenerator.generate(operation1));

        // check no errors were reported
        expect(screen.getByTestId('download-link')).toHaveProperty('href', 'https://gwlandscape.org.au<mock-value-for-field-"detailedOutputFilePath">');
    });

    it('should run the job when orbitalPeriod is used with no validation errors', async () => {
        expect.hasAssertions();

        jest.spyOn(global, 'scrollTo').mockImplementation();

        render(<NewSingleBinaryJob router={global.router}/>);

        //Clear Separation and add value for OrbitalPeriod to make sure form submits if an input was cleared
        const separationInput = screen.getByTestId('separation');
        const orbitalInput = screen.getByTestId('orbitalPeriod');

        userEvent.clear(separationInput);
        userEvent.type(orbitalInput, '1.3');
        userEvent.clear(screen.getByTestId('velocity1'));
        userEvent.clear(screen.getByTestId('velocity2'));

        await waitFor(() => userEvent.click(screen.getByTestId('submit-btn')));

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        global.environment.mock.resolve(operation, MockPayloadGenerator.generate(operation));

        // check that job ran successfully and plot is generated
        expect(screen.getByTestId('download-link')).toHaveProperty('href', 'https://gwlandscape.org.au<mock-value-for-field-"detailedOutputFilePath">');

        // clear orbital period again
        userEvent.clear(orbitalInput);

        // check no errors on separation
        expect(screen.queryByRole('alert', {name: 'Separation (AU)'})).not.toBeInTheDocument();

        // check no errors on velocity 1
        expect(screen.queryByRole('alert', {name: 'Velocity 1'})).not.toBeInTheDocument();
        // check no errors on velocity 2
        expect(screen.queryByRole('alert', {name: 'Velocity 2'})).not.toBeInTheDocument();
    });
});
