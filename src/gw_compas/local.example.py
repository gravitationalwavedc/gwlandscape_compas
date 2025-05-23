import sys

# Use mysql instead of sqlite. Or don't, I'm not your dad
if "test" not in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "gwlandscape_compas",
            "HOST": "localhost",
            "USER": "gwlandscape",
            "PORT": 3306,
            "PASSWORD": "asdf1234",
        },
    }


# Add a valid JWT secret from the job controller if you want to be able to query/create jobs
JOB_CONTROLLER_JWT_SECRET = "<changeme>"

# If you're running the adacs-sso auth host on the same host (localhost)
# you'll want to change the SESSION_COOKIE_NAME, otherwise the sessions
# will overwrite one another
SESSION_COOKIE_NAME = "gwlandscape_compas_session"

# Set the secret to connect to the auth host
ADACS_SSO_CLIENT_SECRET = "gwlandscape_compas_dev_secret"
