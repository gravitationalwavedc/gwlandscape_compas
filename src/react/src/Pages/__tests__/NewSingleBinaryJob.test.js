import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { screen, render, fireEvent, waitFor } from '@testing-library/react';
import NewSingleBinaryJob from '../NewSingleBinaryJob';
import 'regenerator-runtime/runtime';
import userEvent from '@testing-library/user-event';
import { graphql, QueryRenderer } from 'react-relay';

/* global environment, router */

describe('new single binary job page', () => {
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query NewSingleBinaryJobTestQuery @relay_test_operation {
                ...NewSingleBinaryJob_data
                }
            `}
            render={({error, props}) => {
                if(props) {
                    return <NewSingleBinaryJob data={props} router={router} />;
                } else if (error) {
                    return error.message;
                }
            }}
        />
    );

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

        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation)
        ));

        const separationInput = screen.getByTestId('separation');
        const orbitalInput = screen.getByTestId('orbitalPeriod');

        await waitFor(() => user.clear(separationInput));
        await waitFor(() => user.type(orbitalInput, '1.3'));
        await waitFor(() => user.click(screen.getByText('Reset Form')));

        expect(separationInput).toHaveValue(3.5);
        expect(orbitalInput).toHaveValue(null);
    });

    it('should display error message when error is reported from backend', async () => {
        expect.hasAssertions();

        const user = userEvent.setup();
        render(<TestRenderer />);
        await waitFor(() => environment.mock.resolveMostRecentOperation(operation =>
            MockPayloadGenerator.generate(operation)
        ));
        await waitFor(() => user.click(screen.getByTestId('submit-btn')));

        const operation = await waitFor(() => environment.mock.getMostRecentOperation());

        await waitFor(() => environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation, mockNewSingleBinaryResult)
        ));

        const error = await waitFor(() => screen.getByTestId('error-message'));

        expect(error).toHaveTextContent(/Output file failed to generate and returned an empty string/);
    });
});
