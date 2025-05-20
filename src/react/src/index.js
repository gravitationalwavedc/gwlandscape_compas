import './assets/styles.scss';
import getRoutes from './Routes';
import environment from './environment';

let harnessApi = {
  hasAuthToken: () => true,
  getEnvironment: () => environment,
};

function setHarnessApi(api) {
  harnessApi = api;

}

export { getRoutes, setHarnessApi, harnessApi };
