import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import {screen, render, fireEvent, waitFor, act} from '@testing-library/react';
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

        await waitFor(() => {
            render(<NewSingleBinaryJob router={global.router}/>);
            fireEvent.click(screen.getByText('Submit your job'));
        });

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        await waitFor(() => {
            global.environment.mock.resolve(operation, MockPayloadGenerator.generate(operation));
        });

        expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 2000);
        expect(screen.getAllByText('Loading...')).toHaveLength(3);

        await waitFor(() => {
            jest.advanceTimersByTime(2000);
        });

        expect(mockRequest.open).toHaveBeenNthCalledWith(1, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"vanPlotFilePath">', false);
        expect(mockRequest.open).toHaveBeenNthCalledWith(2, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"plotFilePath">', false);

        await waitFor(() => {
            jest.advanceTimersByTime(2000);
        });

        expect(mockRequest.open).toHaveBeenNthCalledWith(3, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"vanPlotFilePath">', false);
        expect(mockRequest.open).toHaveBeenNthCalledWith(4, 'HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"plotFilePath">', false);

        expect(screen.getByTestId('download-link')).toBeTruthy();
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
            };
        }
    };

    it('error message is displayed when error is reported from backend', async () => {
        expect.hasAssertions();

        act(() => {
            render(<NewSingleBinaryJob router={global.router}/>);
            fireEvent.click(screen.getByText('Submit your job'));
        });

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        act(() => {
            global.environment.mock.resolve(
                operation,
                MockPayloadGenerator.generate(operation, mockNewSingleBinaryResult)
            );
        });

        expect(screen.getByTestId('error-msg')).toHaveTextContent('Output could not be generated');
    });

    it('test output files have been generated successfully', async () => {
        expect.hasAssertions();

        jest.useFakeTimers();
        jest.spyOn(global, 'scrollTo').mockImplementation();

        const mockRequest = mockXMLHttpRequest(200);

        act(() => {
            render(<NewSingleBinaryJob router={global.router}/>);
            fireEvent.click(screen.getByText('Submit your job'));
        });

        const operation = await waitFor(() => global.environment.mock.getMostRecentOperation());
        act(() => {
            global.environment.mock.resolve(
                operation,
                MockPayloadGenerator.generate(operation)
            );
            jest.advanceTimersByTime(6000);
        });

        const req = new XMLHttpRequest();
        req.open('HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"vanPlotFilePath">', false);
        req.send();
        expect(req).toEqual(mockRequest);

        req.open('HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"plotFilePath">', false);
        req.send();
        expect(req).toEqual(mockRequest);

        req.open('HEAD', 'https://gwlandscape.org.au<mock-value-for-field-"detailedOutputFilePath">', false);
        req.send();
        expect(req).toEqual(mockRequest);

        expect(screen.getByTestId('van-plot')).toHaveProperty('src', 'https://gwlandscape.org.au<mock-value-for-field-"vanPlotFilePath">');
        expect(screen.getByTestId('detailed-plot')).toHaveProperty('src', 'https://gwlandscape.org.au<mock-value-for-field-"plotFilePath">');
        expect(screen.getByTestId('download-link')).toHaveProperty('href', 'https://gwlandscape.org.au<mock-value-for-field-"detailedOutputFilePath">');

        // jest.clearAllTimers();
        act(() => {
            fireEvent.click(screen.getByText('Submit your job'));
        });

        const operation1 = await waitFor(() => global.environment.mock.getMostRecentOperation());
        await waitFor(() => {
            global.environment.mock.resolve(operation1, MockPayloadGenerator.generate(operation1));
        });

        expect(screen.getAllByText('Loading...')).toHaveLength(3);

        expect(screen.queryByTestId('van-plot')).not.toBeInTheDocument();
        expect(screen.queryByTestId('detailed-plot')).not.toBeInTheDocument();
        expect(screen.queryByTestId('download-link')).not.toBeInTheDocument();

        jest.useRealTimers();
    });
});

