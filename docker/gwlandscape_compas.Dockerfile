FROM python:3.12 as base

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV /venv
ENV COMPAS_ROOT_DIR /COMPAS

# Update and install packages
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt-lists/* \
  && apt-get autoremove --purge -y


FROM base AS django-builder

WORKDIR /src

# Install packages specific for the django-builder
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  python3-virtualenv default-libmysqlclient-dev python3-dev build-essential curl


# Create python virtualenv
RUN virtualenv -p python3 /venv

# Install normal pip requirements
COPY src/requirements.txt ./
RUN ${VIRTUAL_ENV}/bin/pip install -r requirements.txt && ${VIRTUAL_ENV}/bin/pip install mysqlclient gunicorn

# Install COMPAS
WORKDIR /
RUN git clone https://github.com/TeamCOMPAS/COMPAS.git
WORKDIR /COMPAS
RUN ${VIRTUAL_ENV}/bin/pip install .

# Copy the source code in to the container
COPY src /src

# Get rid of an already existing venv if it's there
RUN rm -rf /src/venv

WORKDIR /src
# Generate graphql schema
RUN ${VIRTUAL_ENV}/bin/python development-manage.py graphql_schema

# Clean up unneeded packages and files
RUN apt-get remove --purge -y build-essential python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt-lists/* \
  && apt-get autoremove --purge -y



# Set the working directory and start script
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"


FROM base AS django-runner

ENV DJANGO_SETTINGS_MODULE gw_compas.production-settings

COPY --from=django-builder /src /src
COPY --from=django-builder /venv /venv

# Don't need any of the javascipt code now
RUN rm -Rf /src/react

# Include runserver
COPY ./runserver.sh /runserver.sh
RUN chmod +x /runserver.sh

# Expose the port and set the run script
EXPOSE 8000

WORKDIR /src
CMD [ "/runserver.sh" ]


FROM node:24.1.0 AS react-builder

# Copy react source in
WORKDIR /react
COPY ./src/react /react

COPY --from=django-builder /src/react/data/schema.graphql /react/data/schema.graphql

RUN npm install \
  && npm run relay \
  && npm run build

FROM nginx:1.27.5 as static-runner
COPY --from=react-builder /react/dist /static

COPY ./nginx/nginx.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 8000
