import graphene
from django.conf import settings
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, user_passes_test
from graphql_relay import from_global_id

from publications.models import Keyword


def check_publication_management_user(user):
    return user.user_id in settings.PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS


class KeywordNode(DjangoObjectType):
    """
    Type for Keywords without authentication
    """
    class Meta:
        model = Keyword
        fields = ['tag']
        interfaces = (relay.Node,)


class Query(object):
    keywords = relay.Node.Field(KeywordNode)


class AddKeywordMutation(relay.ClientIDMutation):
    class Input:
        tag = graphene.String()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, tag):
        Keyword.create_keyword(tag)
        return AddKeywordMutation(result=True)


class DeleteKeywordMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        Keyword.delete_keyword(from_global_id(id)[1])
        return AddKeywordMutation(result=True)


class Mutation(graphene.ObjectType):
    add_keyword = AddKeywordMutation.Field()
    delete_keyword = DeleteKeywordMutation.Field()
