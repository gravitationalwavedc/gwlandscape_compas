import traceback
from _decimal import Decimal
from pathlib import Path

import django_filters
import graphene
from django_filters import FilterSet, OrderingFilter
from django.conf import settings
from graphene import relay
from graphql import GraphQLError
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_relay.node.node import from_global_id, to_global_id

from .models import CompasJob, Label, SingleBinaryJob, FileDownloadToken
from .types import OutputStartType, JobStatusType, AbstractBasicParameterType, AbstractAdvancedParametersType
from .views import create_compas_job, update_compas_job, create_single_binary_job
from .utils.derive_job_status import derive_job_status
from .utils.jobs.request_job_filter import request_job_filter
from .utils.h5ToJson import read_h5_data_as_json
from .utils.jobs.request_file_download_id import request_file_download_id
from .utils.auth.lookup_users import request_lookup_users
from .utils.db_search.db_search import perform_db_search
from .status import JobStatus


def basic_parameter_resolvers(name):
    def func(parent, info):
        try:
            param = parent.basic_parameter.get(name=name)
            if param.value in ['true', 'True']:
                return True
            elif param.value in ['false', 'False']:
                return False
            else:
                return param.value

        except parent.basic_parameter.model.DoesNotExist:
            return None
    return func


def advanced_parameter_resolvers(name):
    def func(parent, info):
        try:
            param = parent.advanced_parameter.get(name=name)
            if param.value in ['true', 'True']:
                return True
            elif param.value in ['false', 'False']:
                return False
            else:
                return param.value

        except parent.advanced_parameter.model.DoesNotExist:
            return None
    return func


# Used to give values to fields in a DjangoObjectType, if the fields were not present in the Django model
# Specifically used here to get values from the parameter models
def populate_fields(object_to_modify, field_list, resolver_func):
    for name in field_list:
        setattr(object_to_modify, 'resolve_{}'.format(name), staticmethod(resolver_func(name)))


class LabelType(DjangoObjectType):
    class Meta:
        model = Label
        interfaces = (relay.Node,)


class UserCompasJobFilter(FilterSet):
    class Meta:
        model = CompasJob
        fields = '__all__'

    order_by = OrderingFilter(
        fields=(
            ('last_updated', 'last_updated'),
            ('name', 'name'),
        )
    )

    @property
    def qs(self):
        return CompasJob.user_compas_job_filter(super(UserCompasJobFilter, self).qs, self)


class CompasJobNode(DjangoObjectType, AbstractBasicParameterType, AbstractAdvancedParametersType):
    class Meta:
        model = CompasJob
        convert_choices_to_enum = False
        interfaces = (relay.Node,)

    user = graphene.String()
    job_status = graphene.Field(JobStatusType)
    last_updated = graphene.String()
    start = graphene.Field(OutputStartType)

    @classmethod
    def get_queryset(parent, queryset, info):
        return CompasJob.compas_job_filter(queryset, info)

    def resolve_last_updated(parent, info):
        return parent.last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")

    def resolve_start(parent, info):
        return {
            "name": parent.name,
            "description": parent.description,
            "private": parent.private,
            # "detailed_output": parent.detailed_output
        }

    def resolve_job_status(parent, info):
        try:
            # Get job details from the job controller git commit
            _, jc_jobs = request_job_filter(
                info.context.user.user_id,
                ids=[parent.job_controller_id]
            )

            status_number, status_name, status_date = derive_job_status(jc_jobs[0]["history"])

            return {
                "name": status_name,
                "number": status_number,
                "date": status_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        except Exception:
            return {
                "name": "Unknown",
                "number": 0,
                "data": "Unknown"
            }

    @login_required
    def resolve_user(parent, info):
        success, users = request_lookup_users([parent.user_id], info.context.user.user_id)
        if success and users:
            return f"{users[0]['firstName']} {users[0]['lastName']}"
        return "Unknown User"


populate_fields(
    CompasJobNode,
    [
        "number_of_systems",
        "min_initial_mass",
        "max_initial_mass",
        "initial_mass_function",
        "initial_mass_power",
        "min_metallicity",
        "max_metallicity",
        "metallicity_distribution",
        "min_mass_ratio",
        "max_mass_ratio",
        "mass_ratio_distribution",
        "min_semi_major_axis",
        "max_semi_major_axis",
        "semi_major_axis_distribution",
        "min_orbital_period",
        "max_orbital_period",
        "detailed_output",
    ],
    basic_parameter_resolvers
)

populate_fields(
    CompasJobNode, [
        "mass_transfer_angular_momentum_loss_prescription",
        "mass_transfer_accretion_efficiency_prescription",
        "mass_transfer_fa",
        "common_envelope_alpha",
        "common_envelope_lambda_prescription",
        "remnant_mass_prescription",
        "fryer_supernova_engine",
        "kick_velocity_distribution",
        "velocity_1",
        "velocity_2"
    ],
    advanced_parameter_resolvers
)


class SingleBinaryJobFilter(django_filters.FilterSet):
    class Meta:
        model = SingleBinaryJob
        fields = '__all__'


class SingleBinaryJobNode(DjangoObjectType):
    """
    Type for Single Binary Jobs without authentication
    """
    class Meta:
        model = SingleBinaryJob
        fields = '__all__'
        interfaces = (relay.Node,)


class UserDetails(graphene.ObjectType):
    username = graphene.String()

    def resolve_username(parent, info):
        return "Todo"


class CompasResultFile(graphene.ObjectType):
    path = graphene.String()
    is_dir = graphene.Boolean()
    file_size = graphene.Decimal()
    download_token = graphene.String()


class CompasResultFiles(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    class Input:
        job_id = graphene.ID()

    files = graphene.List(CompasResultFile)


class CompasPublicJobNode(graphene.ObjectType):
    user = graphene.String()
    job_status = graphene.Field(JobStatusType)
    name = graphene.String()
    description = graphene.String()
    id = graphene.ID()
    timestamp = graphene.String()


class CompasPublicJobConnection(relay.Connection):
    class Meta:
        node = CompasPublicJobNode


class Query(object):
    compas_job = relay.Node.Field(CompasJobNode)
    compas_jobs = DjangoFilterConnectionField(CompasJobNode, filterset_class=UserCompasJobFilter)
    all_labels = graphene.List(LabelType)
    compas_result_files = graphene.Field(CompasResultFiles, job_id=graphene.ID(required=True))
    public_compas_jobs = relay.ConnectionField(
        CompasPublicJobConnection,
        search = graphene.String()
    )
    gwclouduser = graphene.Field(UserDetails)

    single_binary_job = relay.Node.Field(SingleBinaryJobNode)
    single_binary_jobs = DjangoFilterConnectionField(SingleBinaryJobNode, filterset_class=SingleBinaryJobFilter)

    # @login_required
    # def resolve_all_labels(self, info, **kwargs):
    #     return Label.all()

    @login_required
    def resolve_gwclouduser(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_compas_result_files(self, info, **kwargs):
        _, job_id = from_global_id(kwargs.get("job_id"))

        job = CompasJob.get_by_id(job_id, info.context.user)
        success, files = job.get_file_list()

        if not success:
            raise Exception("Error getting file list. " + str(files))

        paths = [f['path'] for f in filter(lambda x: not x['isDir'], files)]
        tokens = FileDownloadToken.create(job, paths)

        token_dict = {tok.path: tok.token for tok in tokens}
        result = [
            CompasResultFile(
                path=f['path'],
                is_dir=f['isDir'],
                file_size=Decimal(f['fileSize']),
                download_token=token_dict.get(f['path'], None)
            )
            for f in files
        ]
        return CompasResultFiles(files=result)

    @login_required
    def resolve_public_compas_jobs(self, info, **kwargs):

        success, jobs = perform_db_search(info.context.user, kwargs)
        if not success:
            return []

        result = []
        for job in jobs:
            CompasPublicJobNode(
                user=f"{job['user']['firstName']} {job['user']['lastName']}",
                name=job['job']['name'],
                description=job['job']['description'],
                job_status=JobStatusType(
                    name=JobStatus.display_name(job['history'][0]['state']),
                    number=job['history'][0]['state'],
                    date=job['history'][0]['timestamp']
                ),
                timestamp=job['history'][0]['timestamp'],
                id=to_global_id("CompasJobNode", job['job']['id'])
            )

        return result


class StartInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    private = graphene.Boolean()
    # detailed_output = graphene.Boolean()


class BasicParametersInput(graphene.InputObjectType):
    number_of_systems = graphene.String()
    min_initial_mass = graphene.String()
    max_initial_mass = graphene.String()
    initial_mass_function = graphene.String()
    initial_mass_power = graphene.String()
    min_metallicity = graphene.String()
    max_metallicity = graphene.String()
    metallicity_distribution = graphene.String()
    min_mass_ratio = graphene.String()
    max_mass_ratio = graphene.String()
    mass_ratio_distribution = graphene.String()
    min_semi_major_axis = graphene.String()
    max_semi_major_axis = graphene.String()
    semi_major_axis_distribution = graphene.String()
    min_orbital_period = graphene.String()
    max_orbital_period = graphene.String()
    detailed_output = graphene.String()


class AdvancedParametersInput(graphene.InputObjectType):
    mass_transfer_angular_momentum_loss_prescription = graphene.String()
    mass_transfer_accretion_efficiency_prescription = graphene.String()
    mass_transfer_fa = graphene.String()
    common_envelope_alpha = graphene.String()
    common_envelope_lambda_prescription = graphene.String()
    remnant_mass_prescription = graphene.String()
    fryer_supernova_engine = graphene.String()
    kick_velocity_distribution = graphene.String()
    velocity_1 = graphene.String()
    velocity_2 = graphene.String()


class CompasJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()


class SingleBinaryJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()
    json_data = graphene.String()
    detailed_output_file_path = graphene.String()


class CompasJobMutation(relay.ClientIDMutation):
    class Input:
        start = StartInput()
        basic_parameters = BasicParametersInput()
        advanced_parameters = AdvancedParametersInput()

    result = graphene.Field(CompasJobCreationResult)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, start, basic_parameters, advanced_parameters):
        # Check job name is already used
        existing_job = CompasJob.get_by_name(info.context.user, start.name)
        if existing_job is not None:
            err_msg = "Job name is already in use!"
            print(err_msg)
            raise Exception(err_msg)

        # Create the compas job
        compas_job = create_compas_job(info.context.user, start, basic_parameters, advanced_parameters)

        # Convert the compas job id to a global id
        job_id = to_global_id("CompasJobNode", compas_job.id)

        # Return the compas job id to the client
        return CompasJobMutation(
            result=CompasJobCreationResult(job_id=job_id)
        )


class UpdateCompasJobMutation(relay.ClientIDMutation):
    class Input:
        job_id = graphene.ID(required=True)
        private = graphene.Boolean(required=False)
        labels = graphene.List(graphene.String, required=False)

    result = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        job_id = kwargs.pop("job_id")

        # Update privacy of compas job
        message = update_compas_job(from_global_id(job_id)[1], info.context.user, **kwargs)

        # Return the compas job id to the client
        return UpdateCompasJobMutation(
            result=message
        )


class GenerateFileDownloadIds(relay.ClientIDMutation):
    """
    Copied from GWLab
    """
    class Input:
        job_id = graphene.ID(required=True)
        download_tokens = graphene.List(graphene.String, required=True)

    result = graphene.List(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, root, info, job_id, download_tokens):
        user = info.context.user
        job = CompasJob.get_by_id(from_global_id(job_id)[1], user)

        # Verify the download tokens and get the paths
        paths = FileDownloadToken.get_paths(job, download_tokens)

        # Check all tokens were found
        if None in paths:
            raise GraphQLError("At least one token was invalid or expired")

        # Request file download ids list
        success, result = request_file_download_id(job, paths)

        if not success:
            raise GraphQLError(result)

        # Return list of file download ids
        return GenerateFileDownloadIds(result=result)


class UniqueNameMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String()

    result = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, name):

        return UniqueNameMutation(result=name)


class SingleBinaryJobMutation(relay.ClientIDMutation):
    class Input:
        # input parameters to create the job
        # better to use a class rather than individually
        mass1 = graphene.Float()
        mass2 = graphene.Float()
        metallicity = graphene.Float()
        eccentricity = graphene.Float()
        separation = graphene.Float()
        orbital_period = graphene.Float()
        velocity_1 = graphene.Float()
        velocity_2 = graphene.Float()
        common_envelope_alpha = graphene.Float()
        common_envelope_lambda_prescription = graphene.String()
        remnant_mass_prescription = graphene.String()
        fryer_supernova_engine = graphene.String()
        kick_velocity_distribution = graphene.String()
        mass_transfer_angular_momentum_loss_prescription = graphene.String()
        mass_transfer_accretion_efficiency_prescription = graphene.String()
        mass_transfer_fa = graphene.Float()

    # single_binary_job = graphene.Field(SingleBinaryJobNode)
    result = graphene.Field(SingleBinaryJobCreationResult)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            job = create_single_binary_job(
                mass1=input.get("mass1"),
                mass2=input.get("mass2"),
                metallicity=input.get("metallicity"),
                eccentricity=input.get("eccentricity"),
                separation=input.get("separation"),
                orbital_period=input.get("orbital_period"),
                velocity_1=input.get("velocity_1"),
                velocity_2=input.get("velocity_2"),
                common_envelope_alpha=input.get('common_envelope_alpha'),
                common_envelope_lambda_prescription=input.get('common_envelope_lambda_prescription'),
                remnant_mass_prescription=input.get('remnant_mass_prescription'),
                fryer_supernova_engine=input.get('fryer_supernova_engine'),
                kick_velocity_distribution=input.get('kick_velocity_distribution'),
                mass_transfer_angular_momentum_loss_prescription=input.get(
                    'mass_transfer_angular_momentum_loss_prescription'),
                mass_transfer_accretion_efficiency_prescription=input.get(
                    'mass_transfer_accretion_efficiency_prescription'),
                mass_transfer_fa=input.get('mass_transfer_fa')
            )

            detailed_output_file_path = \
                Path(settings.COMPAS_IO_PATH) / str(job.id) / 'COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'

            json_data = read_h5_data_as_json(detailed_output_file_path)

            return SingleBinaryJobMutation(
                result=SingleBinaryJobCreationResult(
                    job_id=job.id,
                    json_data=json_data,
                    detailed_output_file_path=f'{settings.MEDIA_URL}jobs/{job.id}'
                                              f'/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'

                )
            )
        except Exception:
            traceback.print_exc()
            print("COMPAS job didn't run successfully")
            return SingleBinaryJobMutation(
                result=SingleBinaryJobCreationResult(
                    job_id='', json_data='', detailed_output_file_path=''))


class Mutation(graphene.ObjectType):
    new_compas_job = CompasJobMutation.Field()
    update_compas_job = UpdateCompasJobMutation.Field()
    generate_file_download_ids = GenerateFileDownloadIds.Field()
    is_name_unique = UniqueNameMutation.Field()
    new_single_binary = SingleBinaryJobMutation.Field()
