from django.test import testcases
from graphql_jwt.testcases import JSONWebTokenClient
from gw_compas.schema import schema
from graphql_jwt.shortcuts import get_token
from graphql_jwt.settings import jwt_settings


class CompasJSONWebTokenClient(JSONWebTokenClient):
    """Compas test client with a custom authentication method."""

    def authenticate(self, user):
        """Payload for authentication in compas requires a special userID parameter."""
        self._credentials = {
            jwt_settings.JWT_AUTH_HEADER_NAME: "{0} {1}".format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX, get_token(user, userId=user.id, isLigo=True)
            ),
        }


class CompasTestCase(testcases.TestCase):
    """
    Compas test classes should inherit from this class.

    It overrides some settings that will be common to most compas test cases.

    Attributes
    ----------

    GRAPHQL_SCHEMA : schema object
        Uses the compas schema file as the default schema.

    GRAPHQL_URL : str
        Sets the graphql url to the current compas url.

    client_class : class
        Sets client to be a special compas specific object that uses a custom authentication.
        method.
    """

    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql"
    client_class = CompasJSONWebTokenClient
    maxDiff = None
