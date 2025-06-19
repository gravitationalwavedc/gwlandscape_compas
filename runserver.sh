#! /bin/bash
/venv/bin/python /src/production-manage.py migrate
/venv/bin/python /src/production-manage.py collectstatic --noinput

/venv/bin/gunicorn gw_compas.wsgi -b 0.0.0.0:8000 --workers 8 --timeout 86400
