FROM python:3.8
ENV PYTHONUNBUFFERED 1

# Update the container and install the required packages
WORKDIR /
RUN apt-get update
RUN apt-get install -y texlive-latex-extra cm-super dvipng
RUN apt-get install -y git g++ libhdf5-serial-dev libboost-all-dev libgsl-dev zip
RUN apt-get -y install python3-virtualenv default-libmysqlclient-dev python3-dev build-essential curl

# Add COMPAS_ROOT_DIR to environment variables. It is required for installing and running COMPAS
ENV COMPAS_ROOT_DIR /COMPAS
ENV VIRTUAL_ENV /src/venv

# Install COMPAS
RUN git clone https://github.com/TeamCOMPAS/COMPAS.git
RUN cd /COMPAS && git checkout tags/v02.27.00
RUN cd /COMPAS/src && make -j`nproc` -f Makefile
WORKDIR /

# Copy the source code in to the container
COPY src /src

# Create python virtualenv
RUN rm -Rf /src/venv
RUN virtualenv -p python3 /src/venv

# Activate and install the django requirements (mysqlclient requires python3-dev and build-essential)
RUN . /src/venv/bin/activate && pip install -r /src/requirements.txt && pip install mysqlclient && pip install gunicorn

# Add virtual env to PATH for celery to be recognised by both celery and django containers
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# Set the working directory and start script
WORKDIR /src

# Make sure we're using the production settings
ENV DJANGO_SETTINGS_MODULE gw_compas.production-settings

CMD ["celery", "-A", "gw_compas.celery", "worker", "-l", "INFO"]
