import React from 'react';
import { setHarnessApi } from './index';
import { render } from '@testing-library/react';
import { createMockEnvironment } from 'relay-test-utils';
import { QueryRenderer } from 'react-relay';

// This ignores the jest global variable from eslint errors.
/* global global */

// Global imports for tests
import '@testing-library/jest-dom/extend-expect';

const environment = createMockEnvironment();

setHarnessApi({
    getEnvironment: () => environment,
    currentUser: {
        userId: 1
    }
});

global.queryRendererSetup = (inputQuery, componentToRender) => {
    render(
        <QueryRenderer
            environment={environment}
            query={inputQuery}
            variables={{}}
            render={({ error, props }) => {
                if (props) {
                    return componentToRender(props);
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );
    return environment;
};

global.router = {
    push: jest.fn(),
    replace: jest.fn(),
    go: jest.fn(),
    createHref: jest.fn(),
    createLocation: jest.fn(),
    isActive: jest.fn(),
    matcher: {
        match: jest.fn(),
        getRoutes: jest.fn(),
        isActive: jest.fn(),
        format: jest.fn()
    },
    addTransitionHook: jest.fn(),
    addNavigationListener: jest.fn()
};

global.environment = environment;

// This leaves behind a warning, but I can't figure out how to get rid of it :(
// eslint-disable-next-line jest/prefer-spy-on
global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    disconnect: jest.fn(),
    unobserve: jest.fn()
}));
