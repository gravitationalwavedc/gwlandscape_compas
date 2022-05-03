import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {render, fireEvent, waitFor, act, getAllByText} from '@testing-library/react';
import NewSingleBinaryJob from '../NewSingleBinaryJob';
import 'regenerator-runtime/runtime';

describe('new single binary job page', () => {
    // it('should render',  async () => {
    //     expect.hasAssertions();
    //     const {getByTestId, getByText, debug} = render(<NewSingleBinaryJob router={router} />);
    //     fireEvent.click(getByText('Submit your job'));
    //     // debug();
    //     const operation = await waitFor(() => environment.mock.getMostRecentOperation());
    //     environment.mock.resolve(
    //         operation,
    //         MockPayloadGenerator.generate(operation)
    //     );
    //     // debug();
    //     expect(getByText('Run COMPAS yourself')).toBeDefined();
    //     // expect(getByTestId('download-link')).toHaveTextContent('Download Output File');
    // });

    it('setInterval is called', async () => {
        jest.useFakeTimers();
        jest.spyOn(global, 'setInterval');
        jest.spyOn(global, 'clearInterval');

        const {getByText, getByTestId, getAllByText} = render(<NewSingleBinaryJob router={router}/>);

        fireEvent.click(getByText('Submit your job'));
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );

        expect(setInterval).toHaveBeenCalled();
        expect(getAllByText('Loading...')).toHaveLength(3);

        jest.runAllTimers();

        expect(getByTestId('download-link')).toBeTruthy();
        jest.useRealTimers();
    });
});



