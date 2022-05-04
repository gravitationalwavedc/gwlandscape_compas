import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {render, fireEvent, waitFor, act} from '@testing-library/react';
import NewSingleBinaryJob from '../NewSingleBinaryJob';
import 'regenerator-runtime/runtime';

/* global global */

const mockXMLHttpRequest = (status) => {
    const mock = {
        open: jest.fn(),
        addEventListener: jest.fn(),
        setRequestHeader: jest.fn(),
        send: jest.fn(),
        getResponseHeader: jest.fn(),

        upload: {
            addEventListener: jest.fn(),
        },

        status: status
    };

    jest.spyOn(global, 'XMLHttpRequest').mockImplementation(() => mock);

    return mock;
};

describe('new single binary job page', () => {
    it('setInterval is called', async () => {
        expect.hasAssertions();

        jest.useFakeTimers();
        jest.spyOn(global, 'setInterval');
        jest.spyOn(global, 'clearInterval');
        jest.spyOn(global, 'scrollTo').mockImplementation();

        const mockRequest = mockXMLHttpRequest(404);
        const {getByText, getByTestId, getAllByText} = render(<NewSingleBinaryJob router={global.router}/>);

        fireEvent.click(getByText('Submit your job'));
        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );

        expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 2000);
        expect(getAllByText('Loading...')).toHaveLength(3);

        act(() => {
            jest.advanceTimersToNextTimer();
        });

        expect(mockRequest.open).toHaveBeenNthCalledWith(1, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"vanPlotFilePath">', false);
        expect(mockRequest.open).toHaveBeenNthCalledWith(2, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"plotFilePath">', false);

        expect(getByTestId('download-link')).toBeTruthy();
        jest.useRealTimers();
    });

    const mockNewSingleBinaryResult = {
        SingleBinaryJobCreationResult() {
            return {
                jobId: '100',
                gridFilePath: '',
                plotFilePath: '',
                vanPlotFilePath: '',
                detailedOutputFilePath: ''
            }
        }
    };

    it('error message is displayed when error is reported from backend', async () => {
        expect.hasAssertions();

        const {getByText, getByTestId} = render(<NewSingleBinaryJob router={global.router}/>);

        fireEvent.click(getByText('Submit your job'));
        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        global.environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation, mockNewSingleBinaryResult)
        );

        expect(getByTestId('error-msg')).toHaveTextContent('Output could not be generated');
    });
});



