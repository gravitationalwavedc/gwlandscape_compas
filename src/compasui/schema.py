import traceback

import django_filters
import graphene
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_relay.node.node import from_global_id, to_global_id

from .models import CompasJob, Label, SingleBinaryJob
from .types import OutputStartType, JobStatusType, AbstractBasicParameterType
from .views import create_compas_job, update_compas_job, create_single_binary_job
from .utils.derive_job_status import derive_job_status
from .utils.jobs.request_job_filter import request_job_filter
from django.conf import settings


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


class CompasJobNode(DjangoObjectType, AbstractBasicParameterType):
    class Meta:
        model = CompasJob
        convert_choices_to_enum = False
        interfaces = (relay.Node,)

    # user = graphene.String()
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
            "private": parent.private
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


populate_fields(
    CompasJobNode,
    [
        "number_of_systems",
        "min_initial_mass",
        "max_initial_mass",
        "initial_mass_function",
        "metallicity",
        "min_metallicity",
        "max_metallicity",
        "metallicity_distribution",
        "min_mass_ratio",
        "max_mass_ratio",
        "mass_ratio_distribution",
        "min_semi_major_axis",
        "max_semi_major_axis",
        "semi_major_axis_distribution"
    ],
    parameter_resolvers
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


class Query(object):
    compas_job = relay.Node.Field(CompasJobNode)
    compas_jobs = DjangoFilterConnectionField(CompasJobNode, filterset_class=UserCompasJobFilter)
    all_labels = graphene.List(LabelType)

    single_binary_job = relay.Node.Field(SingleBinaryJobNode)
    single_binary_jobs = DjangoFilterConnectionField(SingleBinaryJobNode, filterset_class=SingleBinaryJobFilter)

    @login_required
    def resolve_all_labels(self, info, **kwargs):
        return Label.all()

    @login_required
    def resolve_gwclouduser(self, info, **kwargs):
        return info.context.user


class StartInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    private = graphene.Boolean()


class BasicParametersInput(graphene.InputObjectType):
    number_of_systems = graphene.String()
    min_initial_mass = graphene.String()
    max_initial_mass = graphene.String()
    initial_mass_function = graphene.String()
    metallicity = graphene.String()
    min_metallicity = graphene.String()
    max_metallicity = graphene.String()
    metallicity_distribution = graphene.String()
    min_mass_ratio = graphene.String()
    max_mass_ratio = graphene.String()
    mass_ratio_distribution = graphene.String()
    min_semi_major_axis = graphene.String()
    max_semi_major_axis = graphene.String()
    semi_major_axis_distribution = graphene.String()


class CompasJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()


class SingleBinaryJobCreationResult(graphene.ObjectType):
    job_id = graphene.String()
    grid_file_path = graphene.String()
    plot_file_path = graphene.String()
    van_plot_file_path = graphene.String()
    detailed_output_file_path = graphene.String()


class CompasJobMutation(relay.ClientIDMutation):
    class Input:
        start = StartInput()
        basic_parameters = BasicParametersInput()

    result = graphene.Field(CompasJobCreationResult)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, start, basic_parameters):
        # Create the compas job
        compas_job = create_compas_job(info.context.user, start, basic_parameters)

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
                user=info.context.user,
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
            return SingleBinaryJobMutation(
                # single_binary_job=job
                result=SingleBinaryJobCreationResult(
                    job_id=job.id,
                    plot_file_path=f'{settings.MEDIA_URL}jobs/{job.id}'
                                   f'/COMPAS_Output/Detailed_Output/detailedEvolutionPlot.png',
                    grid_file_path=f'{settings.MEDIA_URL}jobs/{job.id}/BSE_grid.txt',
                    van_plot_file_path=f'{settings.MEDIA_URL}jobs/{job.id}'
                                       f'/COMPAS_Output/Detailed_Output/vanDenHeuvalPlot.png',
                    detailed_output_file_path=f'{settings.MEDIA_URL}jobs/{job.id}'
                                              f'/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5'
                )
            )
        except Exception:
            traceback.print_exc()
            print("COMPAS job didn't run successfully")
            return SingleBinaryJobMutation(
                result=SingleBinaryJobCreationResult(
                    job_id='', plot_file_path='', grid_file_path='',
                    van_plot_file_path='', detailed_output_file_path=''))


class Mutation(graphene.ObjectType):
    new_compas_job = CompasJobMutation.Field()
    update_compas_job = UpdateCompasJobMutation.Field()
    is_name_unique = UniqueNameMutation.Field()
    new_single_binary = SingleBinaryJobMutation.Field()
