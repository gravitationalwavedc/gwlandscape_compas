import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {fireEvent, render, waitFor, screen} from '@testing-library/react';
import NewJob from '../NewJob';
import 'regenerator-runtime/runtime';

/* global router,environment */

const mockReturn = {
    newCompasJob() {
        return null;
    },
    errors(){
        return [{
            message: 'Error submitting job!'
        }];
    }
};

describe('new compas population job page', () => {
    it('should send a mutation when the form is submitted', async () => {
        expect.hasAssertions();
        render(<NewJob router={router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(router.replace).toHaveBeenCalledWith('/compas/job-results/<mock-value-for-field-"jobId">/');
    });

    it('should show Accretion Efficiency when Accretion Efficiency Prescription has FIXED selected', () => {
        expect.hasAssertions();
        const {getByLabelText} = render(<NewJob router={router}/>);

        expect(getByLabelText('Initial Mass Power').closest('div')).toHaveClass('hidden', false);
        fireEvent.change(getByLabelText('Initial Mass Function'), {target: {value:'POWERLAW'}});
        expect(getByLabelText('Initial Mass Power').closest('div')).not.toHaveClass('hidden');

        expect(getByLabelText('Min Mass Ratio').closest('div')).not.toHaveClass('hidden');
        expect(getByLabelText('Max Mass Ratio').closest('div')).not.toHaveClass('hidden');
        fireEvent.change(getByLabelText('Mass Ratio Distribution'), {target: {value:'DUQUENNOYMAYOR1991'}});
        expect(getByLabelText('Min Mass Ratio').closest('div')).toHaveClass('hidden', false);
        expect(getByLabelText('Max Mass Ratio').closest('div')).toHaveClass('hidden', false);

        expect(getByLabelText('Min Metallicity').closest('div')).toHaveClass('hidden', false);
        expect(getByLabelText('Max Metallicity').closest('div')).toHaveClass('hidden', false);
        fireEvent.change(getByLabelText('Metallicity Distribution'), {target: {value:'LOGUNIFORM'}});
        expect(getByLabelText('Min Metallicity').closest('div')).not.toHaveClass('hidden');
        expect(getByLabelText('Max Metallicity').closest('div')).not.toHaveClass('hidden');

        expect(getByLabelText('Fraction Accreted').closest('div')).toHaveClass('hidden', false);
        fireEvent.change(getByLabelText('Accretion Efficiency Prescription'), {target: {value:'FIXED'}});
        expect(getByLabelText('Fraction Accreted').closest('div')).not.toHaveClass('hidden');

        expect(getByLabelText('Fryer Supernova Engine').closest('div')).not.toHaveClass('hidden');
        fireEvent.change(getByLabelText('Remnant Mass Prescription'), { target: { value: 'HURLEY2000'}});
        expect(getByLabelText('Fryer Supernova Engine').closest('div')).toHaveClass('hidden', false);

        expect(getByLabelText('Velocity 1 (km/s)').closest('div')).toHaveClass('hidden', false);
        expect(getByLabelText('Velocity 2 (km/s)').closest('div')).toHaveClass('hidden', false);
        fireEvent.change(getByLabelText('Kick Velocity Distribution'), {target: {value:'FIXED'}});
        expect(getByLabelText('Velocity 1 (km/s)').closest('div')).not.toHaveClass('hidden');
        expect(getByLabelText('Velocity 2 (km/s)').closest('div')).not.toHaveClass('hidden');

    });

    it('should display error message if job is not submitted' , async () => {
        expect.hasAssertions();
        render(<NewJob router={router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));
        await waitFor(() =>
            environment.mock.resolveMostRecentOperation(() => ({
                errors:[
                    {message: 'Error...'}
                ],
                data: {
                    newCompasJob: null
                }
            })));
        expect(screen.getByTestId('error-msg')).toBeInTheDocument();
        expect(screen.getByTestId('error-msg')).toHaveTextContent('Error submitting job!');
    });

    it('should display error message if job name is not unique', async () => {
        expect.hasAssertions();
        render(<NewJob router={router}/>);
        fireEvent.click(screen.getByTestId('submit-btn'));
        await waitFor(() =>
            environment.mock.resolveMostRecentOperation(() => ({
                errors:[
                    {message: 'UNIQUE constraint'}
                ],
                data: {
                    newCompasJob: null
                }
            })));
        expect(screen.getByTestId('error-msg')).toBeInTheDocument();
        expect(screen.getByTestId('error-msg')).toHaveTextContent('Job name is already in use!');
    });

});
