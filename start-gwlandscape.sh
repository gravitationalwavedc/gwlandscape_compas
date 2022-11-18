#!/bin/bash
cd ~/PycharmProjects/GWLandscape/gwcloud-react-host/src
nvm use
npm run start_gwlandscape &

cd ~/PycharmProjects/GWLandscape/gwcloud-auth/src
venv/bin/python development-manage.py runserver 8000 &

cd ~/PycharmProjects/GWLandscape/gwcloud-auth/src/react/src
nvm use
npm run start &

cd ~/PycharmProjects/GWLandscape/gwlandscape-compas/src/react/src
nvm use
npm run start &

cd ~/PycharmProjects/GWLandscape/gwlandscape-compas/src
venv/bin/python development-manage.py runserver 8003

