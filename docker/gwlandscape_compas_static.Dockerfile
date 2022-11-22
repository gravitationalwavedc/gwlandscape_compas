FROM nginx:latest

# Install needed packages
RUN apt-get update
RUN apt-get install -y curl git python3 python3-virtualenv rsync

# Copy the compas source code in to the container
COPY src /src
# add COMPAS_ROOT_DIR variable so that compose stop complaining about it when parsing COMPAS scripts
ENV COMPAS_ROOT_DIR /COMPAS

# Pull down and set up the compas repo
RUN cd /tmp && rsync -arv /src /tmp/gwlandscape-compas/
WORKDIR /tmp/gwlandscape-compas/src
RUN virtualenv -p python3 venv
RUN venv/bin/pip install -r requirements.txt
RUN mkdir -p logs
# Build the graphql schema from the compas repo
RUN venv/bin/python development-manage.py graphql_schema

# Copy the compas source in to the container
WORKDIR /

# Copy the generate compas schema
RUN mkdir -p /gwlandscape-compas/src/react/data/
RUN mv /tmp/gwlandscape-compas/src/react/data/schema.json /src/react/data/

# Don't need the compas project now
RUN rm -Rf /tmp/gwlandscape-compas

# Build webpack bundle
RUN mkdir /src/static
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
RUN . ~/.nvm/nvm.sh && cd /src/react/ && nvm install && nvm use && npm install npm@8.5.5 && npm install && npm run relay && npm run build

# Copy the javascript bundle
RUN rsync -arv /src/static/ /static/

# Don't need any of the javascipt code now
RUN rm -Rf /src
RUN rm -Rf ~/.nvm/

RUN apt-get remove -y --purge python3 python-virtualenv rsync
RUN apt-get autoremove --purge -y

ADD ./nginx/static.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 8000
