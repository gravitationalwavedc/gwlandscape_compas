from decimal import Decimal
from pathlib import Path

import h5py

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, user_passes_test
from graphql_relay import from_global_id, to_global_id

from publications.models import Keyword, CompasPublication, CompasModel, CompasDatasetModel, \
    CompasDatasetModelUploadToken, FileDownloadToken
from publications.utils.misc import check_publication_management_user
from publications.utils.h5_functions import get_h5_subgroup_meta, get_h5_subgroup_data


class KeywordNode(DjangoObjectType):
    """
    Type for Keywords without authentication
    """
    class Meta:
        model = Keyword
        fields = ['tag']
        filter_fields = {
            'id': ['exact'],
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
            'dataset_models',
            'creation_time',
            'description',
            'public',
            'download_link',
            'arxiv_id',
            'keywords'
        ]
        filter_fields = {
            'id': ['exact'],
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
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'summary': ['exact', 'icontains'],
            'description': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class PlotDataType(graphene.ObjectType):
    log_check_x = graphene.Boolean()
    log_check_y = graphene.Boolean()
    min_max_x = graphene.List(graphene.Float)
    min_max_y = graphene.List(graphene.Float)
    null_check_x = graphene.Boolean()
    null_check_y = graphene.Boolean()
    sides = graphene.List(graphene.Float)
    hist_data = graphene.String()
    scatter_data = graphene.String()


class PlotMetaType(graphene.ObjectType):
    groups = graphene.List(graphene.String)
    group = graphene.String()
    subgroups = graphene.List(graphene.String)
    subgroup_x = graphene.String()
    subgroup_y = graphene.String()
    stride_length = graphene.Int()
    total_length = graphene.Int()


class DatasetFile(graphene.ObjectType):
    path = graphene.String()
    file_size = graphene.Decimal()
    download_token = graphene.String()


class CompasDatasetModelNode(DjangoObjectType):
    """
    Type for CompasDatasetModel without authentication
    """
    files = graphene.List(DatasetFile)
    data_file = graphene.Field(DatasetFile)
    plot_meta = graphene.Field(
        PlotMetaType,
        root_group=graphene.String(),
        subgroup_x=graphene.String(),
        subgroup_y=graphene.String(),
        stride_length=graphene.Int()
    )
    plot_data = graphene.Field(
        PlotDataType,
        root_group=graphene.String(),
        subgroup_x=graphene.String(),
        subgroup_y=graphene.String(),
        stride_length=graphene.Int()
    )

    class Meta:
        model = CompasDatasetModel
        fields = ['compas_publication', 'compas_model']
        filter_fields = {
            'id': ['exact'],
            'compas_publication': ['exact'],
            'compas_model': ['exact']
        }
        interfaces = (relay.Node,)

    def resolve_files(root, info, **kwargs):
        paths = [Path(f.file.path).absolute() for f in root.upload_set.all()]
        tokens = FileDownloadToken.create(root, paths)

        # Generate a dict that can be used to query the generated tokens
        token_dict = {tk.path: tk.token for tk in tokens}

        # Build the resulting file list and send it back to the client
        return [
            DatasetFile(
                path=path,
                file_size=Decimal(path.stat().st_size),
                download_token=token_dict.get(path, None),
            )
            for path in paths
        ]

    def resolve_data_file(root, info, **kwargs):
        path = Path(root.get_data_file().path).absolute()
        tokens = FileDownloadToken.create(root, [path])

        # Build the resulting file list and send it back to the client
        return DatasetFile(
            path=path,
            file_size=Decimal(path.stat().st_size),
            download_token=tokens[0].token if len(tokens) else None,
        )

    def resolve_plot_meta(root, info, **kwargs):
        f = h5py.File(Path(root.get_data_file().path).absolute())
        return get_h5_subgroup_meta(f, **kwargs)

    def resolve_plot_data(root, info, **kwargs):
        f = h5py.File(Path(root.get_data_file().path).absolute())
        plot_meta = get_h5_subgroup_meta(f, **kwargs)
        return get_h5_subgroup_data(
            f,
            root_group=plot_meta["group"],
            subgroup_x=plot_meta["subgroup_x"],
            subgroup_y=plot_meta["subgroup_y"],
            stride_length=plot_meta["stride_length"]
        )


class GenerateCompasDatasetModelUploadToken(graphene.ObjectType):
    token = graphene.String()


class Query(object):
    keywords = DjangoFilterConnectionField(KeywordNode)
    compas_publication = relay.Node.Field(CompasPublicationNode)
    compas_publications = DjangoFilterConnectionField(CompasPublicationNode)
    compas_models = DjangoFilterConnectionField(CompasModelNode)
    compas_dataset_model = relay.Node.Field(CompasDatasetModelNode)
    compas_dataset_models = DjangoFilterConnectionField(CompasDatasetModelNode)

    generate_compas_dataset_model_upload_token = graphene.Field(GenerateCompasDatasetModelUploadToken)

    @login_required
    @user_passes_test(check_publication_management_user)
    def resolve_generate_compas_dataset_model_upload_token(self, info, **kwargs):
        user = info.context.user

        # Create a compas dataset model upload token
        token = CompasDatasetModelUploadToken.create(user)

        # Return the generated token
        return GenerateCompasDatasetModelUploadToken(token=str(token.token))


class AddKeywordMutation(relay.ClientIDMutation):
    class Input:
        tag = graphene.String(required=True)

    id = graphene.String()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, tag):
        keyword = Keyword.create_keyword(tag)
        return AddKeywordMutation(to_global_id("Keyword", keyword.id))


class DeleteKeywordMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        Keyword.delete_keyword(from_global_id(id)[1])
        return DeleteKeywordMutation(result=True)


class UpdateKeywordMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        tag = graphene.String()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id, tag):
        Keyword.update_keyword(from_global_id(id)[1], tag)
        return UpdateKeywordMutation(result=True)


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

    id = graphene.ID()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, **kwargs):
        keyword_ids = [from_global_id(_id)[1] for _id in kwargs.pop('keywords', [])]
        publication = CompasPublication.create_publication(**kwargs, keywords=keyword_ids)
        return AddPublicationMutation(id=to_global_id('CompasPublicationNode', publication.id))


class DeletePublicationMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id):
        CompasPublication.delete_publication(from_global_id(id)[1])
        return DeletePublicationMutation(result=True)


class UpdatePublicationMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        author = graphene.String()
        # published defines if the job was published in a journal/arxiv
        published = graphene.Boolean()
        title = graphene.String()
        year = graphene.Int()
        journal = graphene.String()
        journal_doi = graphene.String()
        dataset_doi = graphene.String()
        description = graphene.String()
        # public defines if the job is publicly accessible
        public = graphene.Boolean()
        download_link = graphene.String()
        arxiv_id = graphene.String()
        keywords = graphene.List(graphene.String)

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id, **kwargs):
        keyword_ids = [from_global_id(_id)[1] for _id in kwargs.pop('keywords', [])]
        CompasPublication.update_publication(_id=from_global_id(id)[1], **kwargs, keywords=keyword_ids)
        return UpdatePublicationMutation(result=True)


class AddCompasModelMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        summary = graphene.String()
        description = graphene.String()

    id = graphene.ID()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, **kwargs):
        model = CompasModel.create_model(**kwargs)
        return AddCompasModelMutation(id=to_global_id('CompasModelNode', model.id))


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


class UpdateCompasModelMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        summary = graphene.String()
        description = graphene.String()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id, **kwargs):
        CompasModel.update_model(from_global_id(id)[1], **kwargs)
        return UpdateCompasModelMutation(result=True)


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


class UpdateCompasDatasetModelMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        compas_publication = graphene.String()
        compas_model = graphene.String()

    result = graphene.Boolean()

    @classmethod
    @login_required
    @user_passes_test(check_publication_management_user)
    def mutate_and_get_payload(cls, root, info, id, **kwargs):
        if 'compas_publication' in kwargs:
            kwargs['compas_publication'] = CompasPublication.objects.get(
                id=from_global_id(kwargs['compas_publication'])[1]
            )
        if 'compas_model' in kwargs:
            kwargs['compas_model'] = CompasModel.objects.get(
                id=from_global_id(kwargs['compas_model'])[1]
            )
        CompasDatasetModel.update_dataset_model(from_global_id(id)[1], **kwargs)
        return UpdateCompasDatasetModelMutation(result=True)


class UploadCompasDatasetModelMutation(relay.ClientIDMutation):
    class Input:
        upload_token = graphene.String()
        compas_publication = graphene.String(required=True)
        compas_model = graphene.String(required=True)
        job_file = Upload(required=True)

    id = graphene.ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, upload_token, compas_publication, compas_model, job_file):
        # Get the token being used to perform the upload - this will return None if the token doesn't exist or
        # is expired
        token = CompasDatasetModelUploadToken.get_by_token(upload_token)
        if not token:
            raise GraphQLError("Compas Dataset Model upload token is invalid or expired.")

        dataset_model = CompasDatasetModel.create_dataset_model(
            CompasPublication.objects.get(id=from_global_id(compas_publication)[1]),
            CompasModel.objects.get(id=from_global_id(compas_model)[1]),
            job_file
        )

        return UploadCompasDatasetModelMutation(id=to_global_id('CompasDatasetModelNode', dataset_model.id))


class Mutation(graphene.ObjectType):
    add_keyword = AddKeywordMutation.Field()
    delete_keyword = DeleteKeywordMutation.Field()
    update_keyword = UpdateKeywordMutation.Field()
    add_publication = AddPublicationMutation.Field()
    delete_publication = DeletePublicationMutation.Field()
    update_publication = UpdatePublicationMutation.Field()
    add_compas_model = AddCompasModelMutation.Field()
    delete_compas_model = DeleteCompasModelMutation.Field()
    update_compas_model = UpdateCompasModelMutation.Field()
    delete_compas_dataset_model = DeleteCompasDatasetModelMutation.Field()
    update_compas_dataset_model = UpdateCompasDatasetModelMutation.Field()
    upload_compas_dataset_model = UploadCompasDatasetModelMutation.Field()
