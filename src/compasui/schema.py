import os.path

import django.urls
import django_filters
import graphene
import requests
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_relay.node.node import from_global_id, to_global_id

from .models import CompasJob, Label, Data, Search, SingleBinaryJob
from .status import JobStatus
from .types import OutputStartType, JobStatusType, AbstractDataType, AbstractSearchType
from .utils.db_search.db_search import perform_db_search
from .utils.derive_job_status import derive_job_status
from .utils.jobs.request_job_filter import request_job_filter
from .views import create_compas_job, update_compas_job, create_single_binary_job
from django.conf import settings
import os.path


def parameter_resolvers(name):
    def func(parent, info):
        try:
            param = parent.parameter.get(name=name)
            if param.value in ['true', 'True']:
                return True
            elif param.value in ['false', 'False']:
                return False
            else:
                return param.value

        except parent.parameter.model.DoesNotExist:
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
            ('last_updated', 'lastUpdated'),
            ('name', 'name'),
        )
    )

    @property
    def qs(self):
        return CompasJob.user_compas_job_filter(super(UserCompasJobFilter, self).qs, self)


class PublicCompasJobFilter(FilterSet):
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
        return CompasJob.public_compas_job_filter(super(PublicCompasJobFilter, self).qs, self)


class CompasJobNode(DjangoObjectType):
    class Meta:
        model = CompasJob
        convert_choices_to_enum = False
        interfaces = (relay.Node,)

    job_status = graphene.Field(JobStatusType)
    last_updated = graphene.String()
    start = graphene.Field(OutputStartType)
    labels = graphene.List(LabelType)

    @classmethod
    def get_queryset(parent, queryset, info):
        return CompasJob.compas_job_filter(queryset, info)

    def resolve_last_updated(parent, info):
        return parent.last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")

    def resolve_start(parent, info):
        return {
            "name": parent.name,
            "description": parent.description,
            "private": parent.private
        }

    def resolve_labels(parent, info):
        return parent.labels.all()

    def resolve_job_status(parent, info):
        try:
            # Get job details from the job controller
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


class DataType(DjangoObjectType, AbstractDataType):
    class Meta:
        model = Data
        interfaces = (relay.Node,)
        convert_choices_to_enum = False


populate_fields(
    DataType,
    [
        'start_frequency_band',
        'min_start_time',
        'max_start_time',
        'asini',
        'freq_band',
        'alpha',
        'delta',
        'orbit_tp',
        'orbit_period',
        'drift_time',
        'd_freq'
    ],
    parameter_resolvers
)


class SearchType(DjangoObjectType, AbstractSearchType):
    class Meta:
        model = Search
        interfaces = (relay.Node,)
        convert_choices_to_enum = False


populate_fields(
    SearchType,
    [
        'search_start_time',
        'search_t_block',
        'search_central_a0',
        'search_a0_band',
        'search_a0_bins',
        'search_central_p',
        'search_p_band',
        'search_p_bins',
        'search_central_orbit_tp',
        'search_orbit_tp_band',
        'search_orbit_tp_bins',
        'search_l_l_threshold',
    ],
    parameter_resolvers
)


class UserDetails(graphene.ObjectType):
    username = graphene.String()

    def resolve_username(parent, info):
        return "Todo"


class CompasResultFile(graphene.ObjectType):
    path = graphene.String()
    is_dir = graphene.Boolean()
    file_size = graphene.Int()
    download_id = graphene.String()


class CompasResultFiles(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    class Input:
        job_id = graphene.ID()

    files = graphene.List(CompasResultFile)


class CompasPublicJobNode(graphene.ObjectType):
    user = graphene.String()
    name = graphene.String()
    job_status = graphene.Field(JobStatusType)
    labels = graphene.List(LabelType)
    description = graphene.String()
    timestamp = graphene.String()
    id = graphene.ID()


class CompasPublicJobConnection(relay.Connection):
    class Meta:
        node = CompasPublicJobNode


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

class Query(object):
    compas_job = relay.Node.Field(CompasJobNode)
    compas_jobs = DjangoFilterConnectionField(CompasJobNode, filterset_class=UserCompasJobFilter)
    public_compas_jobs = relay.ConnectionField(
        CompasPublicJobConnection,
        search=graphene.String(),
        time_range=graphene.String()
    )

    all_labels = graphene.List(LabelType)

    compas_result_files = graphene.Field(CompasResultFiles, job_id=graphene.ID(required=True))

    gwclouduser = graphene.Field(UserDetails)

    single_binary_job = relay.Node.Field(SingleBinaryJobNode)
    single_binary_jobs = DjangoFilterConnectionField(SingleBinaryJobNode, filterset_class=SingleBinaryJobFilter)

    @login_required
    def resolve_all_labels(self, info, **kwargs):
        return Label.all()

    @login_required
    def resolve_public_compas_jobs(self, info, **kwargs):
        # Perform the database search
        success, jobs = perform_db_search(info.context.user, kwargs)
        if not success:
            return []

        # Parse the result in to graphql objects
        result = []
        for job in jobs:
            result.append(
                CompasPublicJobNode(
                    user=f"{job['user']['firstName']} {job['user']['lastName']}",
                    name=job['job']['name'],
                    description=job['job']['description'],
                    job_status=JobStatusType(
                        name=JobStatus.display_name(job['history'][0]['state']),
                        number=job['history'][0]['state'],
                        date=job['history'][0]['timestamp']
                    ),
                    labels=CompasJob.get_by_id(job['job']['id'], info.context.user).labels.all(),
                    timestamp=job['history'][0]['timestamp'],
                    id=to_global_id("CompasJobNode", job['job']['id'])
                )
            )

        # Nb. The perform_db_search function currently requests one extra record than kwargs['first'].
        # This triggers the ArrayConnection used by returning the result array to correctly set
        # hasNextPage correctly, such that infinite scroll works as expected.
        return result

    @login_required
    def resolve_gwclouduser(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_compas_result_files(self, info, **kwargs):
        # Get the model id of the compas job
        _, job_id = from_global_id(kwargs.get("job_id"))

        # Try to look up the job with the id provided
        job = CompasJob.get_by_id(job_id, info.context.user)

        # Fetch the file list from the job controller
        success, files = job.get_file_list()
        if not success:
            raise Exception("Error getting file list. " + str(files))

        # Build the resulting file list and send it back to the client
        result = []
        for f in files:
            download_id = ""
            if not f["isDir"]:
                # todo: Optimize how file download ids are generated. An id for every file every time
                # todo: the page is loaded is not effective at all
                # Create a file download id for this file
                success, download_id = job.get_file_download_id(f["path"])
                if not success:
                    raise Exception("Error creating file download url. " + str(download_id))

            result.append(
                CompasResultFile(
                    path=f["path"],
                    is_dir=f["isDir"],
                    file_size=f["fileSize"],
                    download_id=download_id
                )
            )

        return CompasResultFiles(files=result)


class StartInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    private = graphene.Boolean()


class DataInput(graphene.InputObjectType):
    data_choice = graphene.String()
    source_dataset = graphene.String()


class DataParametersInput(graphene.InputObjectType):
    start_frequency_band = graphene.String()
    min_start_time = graphene.String()
    max_start_time = graphene.String()
    asini = graphene.String()
    freq_band = graphene.String()
    alpha = graphene.String()
    delta = graphene.String()
    orbit_tp = graphene.String()
    orbit_period = graphene.String()
    drift_time = graphene.String()
    d_freq = graphene.String()


class SearchParametersInput(graphene.InputObjectType):
    search_start_time = graphene.String()
    search_t_block = graphene.String()
    search_central_a0 = graphene.String()
    search_a0_band = graphene.String()
    search_a0_bins = graphene.String()
    search_central_p = graphene.String()
    search_p_band = graphene.String()
    search_p_bins = graphene.String()
    search_central_orbit_tp = graphene.String()
    search_orbit_tp_band = graphene.String()
    search_orbit_tp_bins = graphene.String()
    search_l_l_threshold = graphene.String()


class CompasJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()


class SingleBinaryJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()
    grid_file_path = graphene.String()
    plot_file_path = graphene.String()
    van_plot_file_path = graphene.String()
    run_details_path = graphene.String()


class CompasJobMutation(relay.ClientIDMutation):
    class Input:
        start = StartInput()
        data = DataInput()
        data_parameters = DataParametersInput()
        search_parameters = SearchParametersInput()

    result = graphene.Field(CompasJobCreationResult)

    @classmethod
    def mutate_and_get_payload(cls, root, info, start, data, data_parameters, search_parameters):
        # Create the compas job
        compas_job = create_compas_job(info.context.user, start, data, data_parameters, search_parameters)

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
        velocity_random_number_1 = graphene.Float()
        velocity_random_number_2 = graphene.Float()
        velocity_1 = graphene.Float()
        velocity_2 = graphene.Float()
        theta_1 = graphene.Float()
        theta_2 = graphene.Float()
        phi_1 = graphene.Float()
        phi_2 = graphene.Float()
        mean_anomaly_1 = graphene.Float()
        mean_anomaly_2 = graphene.Float()


    # single_binary_job = graphene.Field(SingleBinaryJobNode)
    result = graphene.Field(SingleBinaryJobCreationResult)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        job = create_single_binary_job(
            mass1=input.get("mass1"),
            mass2=input.get("mass2"),
            metallicity=input.get("metallicity"),
            eccentricity=input.get("eccentricity"),
            separation=input.get("separation"),
            orbital_period=input.get("orbital_period"),
            velocity_random_number_1=input.get("velocity_random_number_1"),
            velocity_random_number_2=input.get("velocity_random_number_2"),
            theta_1=input.get("theta_1"),
            theta_2=input.get("theta_2"),
            phi_1=input.get("phi_1"),
            phi_2=input.get("phi_2"),
            mean_anomaly_1=input.get("mean_anomaly_1"),
            mean_anomaly_2=input.get("mean_anomaly_2"),

        )
        # run_details = ''
        # run_details_path = f'{settings.MEDIA_ROOT}jobs/{job.id}/COMPAS_Output/Run_Details'
        # print(f'path: {run_details_path}')
        # if os.path.exists(run_details_path):
        #     print('exists')
        # with open(run_details_path, 'r') as f:
        #     run_details = f.read()
        #     print(run_details)

        return SingleBinaryJobMutation(
            # single_binary_job=job
            result=SingleBinaryJobCreationResult(
                job_id=job.id,
                plot_file_path=f'{settings.MEDIA_URL}jobs/{job.id}/COMPAS_Output/Detailed_Output/detailedEvolutionPlot.png',
                grid_file_path=f'{settings.MEDIA_URL}jobs/{job.id}/BSE_grid.txt',
                van_plot_file_path=f'{settings.MEDIA_URL}jobs/{job.id}/COMPAS_Output/Detailed_Output/vanDenHeuvalPlot.png',
                run_details_path=f'{settings.MEDIA_URL}jobs/{job.id}/COMPAS_Output/Run_Details'
            )
        )


class Mutation(graphene.ObjectType):
    new_compas_job = CompasJobMutation.Field()
    update_compas_job = UpdateCompasJobMutation.Field()
    is_name_unique = UniqueNameMutation.Field()
    new_single_binary = SingleBinaryJobMutation.Field()
