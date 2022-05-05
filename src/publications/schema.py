import graphene
from django.conf import settings
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, user_passes_test
from graphql_relay import from_global_id, to_global_id

from publications.models import Keyword, CompasPublication, CompasModel


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


class KeywordConnection(relay.Connection):
    class Meta:
        node = KeywordNode


class Query(object):
    keywords = relay.ConnectionField(KeywordConnection)

    def resolve_keywords(root, info, **kwargs):
        return Keyword.all()


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
        return DeleteKeywordMutation(result=True)


class AddPublicationMutation(relay.ClientIDMutation):
    class Input:
        author = graphene.String(required=True)
        # published defines if the job was published in a journal/arxiv
        published = graphene.Boolean()
        title = graphene.String(required=True)
        year = graphene.Int()
        journal = graphene.String()
        journal_doi = graphene.String()
        dataset_doi = graphene.String()
        description = graphene.String()
        # public defines if the job is publicly accessible
        public = graphene.Boolean()
        download_link = graphene.String()
        arxiv_id = graphene.String(required=True)
        keywords = graphene.List(graphene.String)

    result = graphene.Boolean()
    id = graphene.ID()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, **kwargs):
        publication = CompasPublication.create_publication(**kwargs)
        return AddPublicationMutation(result=True, id=to_global_id('CompasPublication', publication.id))


class DeletePublicationMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        CompasPublication.delete_publication(from_global_id(id)[1])
        return DeletePublicationMutation(result=True)


class AddCompasModelMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String()
        summary = graphene.String()
        description = graphene.String()

    result = graphene.Boolean()
    id = graphene.ID()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, name, summary, description):
        model = CompasModel.create_model(name, summary, description)
        return AddCompasModelMutation(result=True, id=to_global_id('CompasModel', model.id))


class DeleteCompasModelMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        CompasModel.delete_model(from_global_id(id)[1])
        return DeleteCompasModelMutation(result=True)


class Mutation(graphene.ObjectType):
    add_keyword = AddKeywordMutation.Field()
    delete_keyword = DeleteKeywordMutation.Field()
    add_publication = AddPublicationMutation.Field()
    delete_publication = DeletePublicationMutation.Field()
    add_compas_model = AddCompasModelMutation.Field()
    delete_compas_model = DeleteCompasModelMutation.Field()
