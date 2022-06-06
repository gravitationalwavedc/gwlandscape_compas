from pathlib import Path

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required, user_passes_test
from graphql_relay import from_global_id, to_global_id

from publications.models import Keyword, CompasPublication, CompasModel, CompasDatasetModel
from publications.utils import check_publication_management_user


class KeywordNode(DjangoObjectType):
    """
    Type for Keywords without authentication
    """
    class Meta:
        model = Keyword
        fields = ['tag']
        filter_fields = {
            'tag': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class CompasPublicationNode(DjangoObjectType):
    """
    Type for CompasPublication without authentication
    """

    class Meta:
        model = CompasPublication
        fields = [
            'author',
            'published',
            'title',
            'year',
            'journal',
            'journal_doi',
            'dataset_doi',
            'creation_time',
            'description',
            'public',
            'download_link',
            'arxiv_id',
            'keywords'
        ]
        filter_fields = {
            'author': ['exact', 'icontains'],
            'published': ['exact'],
            'title': ['exact', 'icontains'],
            'year': ['exact', 'gt', 'lt', 'gte', 'lte'],
            'journal': ['exact', 'icontains'],
            'journal_doi': ['exact', 'icontains'],
            'dataset_doi': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'public': ['exact']
        }
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(parent, queryset, info):
        # Make sure we filter out any publications that are not public if the current user isn't a publication manager
        return CompasPublication.public_filter(queryset, info)


class CompasModelNode(DjangoObjectType):
    """
    Type for CompasModels without authentication
    """
    class Meta:
        model = CompasModel
        fields = ['name', 'summary', 'description']
        filter_fields = {
            'name': ['exact', 'icontains'],
            'summary': ['exact', 'icontains'],
            'description': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class CompasDatasetModelNode(DjangoObjectType):
    """
    Type for CompasDatasetModel without authentication
    """
    files = graphene.List(graphene.String)

    class Meta:
        model = CompasDatasetModel
        fields = ['compas_publication', 'compas_model']
        filter_fields = {
            'compas_publication': ['exact'],
            'compas_model': ['exact']
        }
        interfaces = (relay.Node,)

    def resolve_files(root, info, **kwargs):
        return [Path(f.file.url).absolute() for f in root.upload_set.all()]


class Query(object):
    keywords = DjangoFilterConnectionField(KeywordNode)
    compas_publications = DjangoFilterConnectionField(CompasPublicationNode)
    compas_models = DjangoFilterConnectionField(CompasModelNode)
    compas_dataset_models = DjangoFilterConnectionField(CompasDatasetModelNode)


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


class AddCompasDatasetModelMutation(relay.ClientIDMutation):
    class Input:
        compas_publication = graphene.String(required=True)
        compas_model = graphene.String(required=True)
        file = Upload(required=True)

    result = graphene.Boolean()
    id = graphene.ID()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, compas_publication, compas_model, file):
        dataset_model = CompasDatasetModel.create_dataset_model(
            CompasPublication.objects.get(id=from_global_id(compas_publication)[1]),
            CompasModel.objects.get(id=from_global_id(compas_model)[1]),
            file
        )
        return AddCompasDatasetModelMutation(result=True, id=to_global_id('CompasDatasetModel', dataset_model.id))


class DeleteCompasDatasetModelMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        CompasDatasetModel.delete_dataset_model(from_global_id(id)[1])
        return DeleteCompasDatasetModelMutation(result=True)


class Mutation(graphene.ObjectType):
    add_keyword = AddKeywordMutation.Field()
    delete_keyword = DeleteKeywordMutation.Field()
    add_publication = AddPublicationMutation.Field()
    delete_publication = DeletePublicationMutation.Field()
    add_compas_model = AddCompasModelMutation.Field()
    delete_compas_model = DeleteCompasModelMutation.Field()
    add_compas_dataset_model = AddCompasDatasetModelMutation.Field()
    delete_compas_dataset_model = DeleteCompasDatasetModelMutation.Field()
