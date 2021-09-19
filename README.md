# GW Landscape - Compas module

GW Landscape Compas module for running Compas jobs from the web.



#### Requirements before you start

* Python 3.8+ with the virtualenv module installed
* Node Version Manager (NVM) installed
* In some instances `npm run relay` may raise an error that requires the `watchman` package to be installed.



## Project Structure

There are two "projects" contained in this repository - one for the Django project (backend), and one for the Node/React/Relay project (frontend).

The frontend is in `gwlandscape-compas/src/react/` and the backend is in `gwlandscape-compas/src/`



## Project Setup

First, check out the [gwcloud-react-host](https://phab.adacs.org.au/source/gwcloud-react-host/) and [gwcloud-auth](https://phab.adacs.org.au/source/gwcloud-auth/) repositories in to the same directory as this project, such that the directory structure looks similar to:

```
gwlandscape/
	gwcloud-react-host/
	gwcloud-auth/
	gwlandscape-compas/
```

Make sure to initialise the git submodules so that arcanist works when required:-

* `cd gwlandscape/gwlandscape-compas/`
* `git submodule update --init --recursive`



#### Python/Django setup

Set up the virtual environments for auth and GW Landscape:

* `cd gwlandscape/gwcloud-auth/src/` 
  * `virtualenv -p python3.8 venv` (or whatever version of python you have installed > 3.8)
  * `source venv/bin/activate`
  * `pip install -r requirements.txt`
  * `python development-manage.py migrate`
  * `python development-manage.py createsuperuser` (Set up whatever user you'd like to use to log in with here)
* `cd gwlandscap/gwlandscape-compas/src/`
  * `virtualenv -p python3.8 venv` (or whatever version of python you have installed > 3.8)
  * `source venv/bin/activate`
  * `pip install -r requirements.txt`
  * `python development-manage.py migrate`

#### Javascript setup

Set up the node environments:

* `cd gwlandscape/gwcloud-react-host/src/`

  * `nvm install $(cat .nvmrc)`
  * `nvm use $(cat .nvmrc)`
  * `npm install`

* `cd gwlandscape/gwcloud-auth/src/react/`

  * `nvm install $(cat .nvmrc)`
  * `nvm use $(cat .nvmrc)`
  * `npm install`

* `cd gwlandscape/gwlandscape-compas/src/react/`

  * `nvm install $(cat .nvmrc)`

  * `nvm use $(cat .nvmrc)`

  * `npm install`

    

## Running the project

The project will require running 2 python Django servers and 3 javascript node servers. All projects use file watchers, if you change code it will restart the server automatically where required. The browser will not automatically refresh however, so the page will need to be refreshed to see changes to javascript code.

First some caveats:-

* Any time changes are made to the graphene schema in python, you need to rebuild the graphql schema for javascript, **this also needs to be executed once before running the project for the first time**
  * `cd gwlandscape/gwcloud-auth/src/` (If it's the first time the project is being run, or if auth has been updated)
  * `./venv/bin/python development-manage.py graphql_schema`
  * `cd gwlandscape/gwlandscape-compas/src/`
  * `./venv/bin/python development-manage.py graphql_schema`
* Any time changes are made to the javascript graphql queries, you need to rebuild the graphql query files, this is not automatic, and may require stopping the node server, generating the graphql files, then starting the node server again.
  * `cd gwlandscape/gwlandscape-compas/src/react`
  * `nvm use`
  * `npm run relay`

#### Start the react host

* `cd gwlandscape/gwcloud-react-host/src/`
* `nvm use`
* `npm run relay`
* `npm run start_gwlandscape` (Will start the react host on port 3000 by default)

#### Start auth

Start Django in a new terminal:

* `cd gwlandscape/gwcloud-auth/src/`
* `source ./venv/bin/activate`
* `python development-manage.py runserver 8000` (auth must always run Django on port 8000)

Start Node in a new terminal:

* `cd gwlandscape/gwcloud-auth/src/react/`
* `nvm use`
* `npm run relay`
* `npm run start` (Will start the auth node server on port 3001 by default)

#### Start GW Landscape

Start Django in a new terminal:

* `cd gwlandscape/gwlandscape-compas/src/`
* `source ./venv/bin/activate`
* `python development-manage.py runserver 8003` (GW Landscape must always run Django on port 8003)

Start Node in a new terminal:

* `cd gwlandscape/gwlandscape-compas/src/react/`
* `nvm use`
* `npm run relay`
* `npm run start` (Will start the GW Landscape node server on port 3004 by default)



(Refer to port mappings used by the react-host for local development in https://phab.adacs.org.au/source/gwcloud-react-host/browse/master/src/src/modules.js)



## Accessing the project

Once the project is running, you should be able to visit http://localhost:3000/ to open the project in a browser.

