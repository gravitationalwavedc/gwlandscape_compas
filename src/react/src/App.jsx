import { createFarceRouter, createRender, makeRouteConfig } from 'found';
import { BrowserProtocol, queryMiddleware } from 'farce';
import getRoutes from './Routes';
import { Resolver } from 'found-relay';
import environment from './environment';
import './assets/styles.scss';
import './assets/scss/theme.scss';

function App() {
    const Router = createFarceRouter({
        historyProtocol: new BrowserProtocol(),
        historyMiddlewares: [queryMiddleware],
        routeConfig: makeRouteConfig(getRoutes()),
        render: createRender({}),
    });
    return <Router resolver={new Resolver(environment)} />;
}

export default App;
