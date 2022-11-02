import math
import os
from pathlib import Path

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .utils import constants
from .utils.jobs.request_file_download_id import request_file_download_id
from .utils.jobs.request_file_list import request_file_list
from .utils.jobs.request_job_status import request_job_status
# from .variables import compas_parameters


class Label(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Label: {self.name}"

    @classmethod
    def all(cls):
        """
        Retrieves all labels

        :return: QuerySet of all Labels
        """
        return cls.objects.all()

    @classmethod
    def filter_by_name(cls, labels):
        """
        Filter all Labels by name in the provided labels

        :param labels: A list of strings representing the label names to match
        :return: QuerySet of filtered Labels
        """
        return cls.objects.filter(name__in=labels)


class CompasJob(models.Model):
    """
    CompasJob model
    """
    user_id = models.IntegerField()
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    creation_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    private = models.BooleanField(default=False)

    job_controller_id = models.IntegerField(default=None, blank=True, null=True)

    labels = models.ManyToManyField(Label)
    # is_ligo_job indicates if the job has been run using proprietary data. If running a real job with GWOSC, this will
    # be set to False, otherwise a real data job using channels other than GWOSC will result in this value being True
    is_ligo_job = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            ('user_id', 'name'),
        )

    def __str__(self):
        return f"Compas Job: {self.name}"

    @property
    def job_status(self):
        return request_job_status(self)

    def get_file_list(self, path='', recursive=True):
        return request_file_list(self, path, recursive)

    def get_file_download_id(self, path):
        return request_file_download_id(self, path)

    def as_json(self):
        basic = {}
        advanced = {}

        # basic parameters
        for p in self.basic_parameter.all():
            basic[p.name] = p.value

        # advanced parameters
        for p in self.advanced_parameter.all():
            advanced[p.name] = p.value

        return dict(
            name=self.name,
            description=self.description,
            basic=basic,
            advanced=advanced
        )

    @classmethod
    def get_by_id(cls, bid, user):
        """
        Get CompasJob by the provided id

        This function will raise an exception if:-
        * the job requested is a ligo job, but the user is not a ligo user
        * the job requested is private an not owned by the requesting user

        :param bid: The id of the CompasJob to return
        :param user: The GWCloudUser instance making the request
        :return: CompasJob
        """
        job = cls.objects.get(id=bid)

        # Ligo jobs may only be accessed by ligo users
        # if job.is_ligo_job and not user.is_ligo:
        #     raise Exception("Permission Denied")

        # Users can only access the job if it is public or the user owns the job
        if job.private and user.user_id != job.user_id:
            raise Exception("Permission Denied")

        return job

    @classmethod
    def user_compas_job_filter(cls, qs, user_job_filter):
        """
        Used by UserCompasJobFilter to filter only jobs owned by the requesting user

        :param qs: The UserCompasJobFilter queryset
        :param user_job_filter: The UserCompasJobFilter instance
        :return: The queryset filtered by the requesting user
        """
        return qs.filter(user_id=user_job_filter.request.user.user_id)

    @classmethod
    def public_compas_job_filter(cls, qs, public_job_filter):
        """
        Used by PublicCompasJobFilter to filter only public jobs

        :param qs: The PublicCompasJobFilter queryset
        :param public_job_filter: The PublicCompasJobFilter instance
        :return: The queryset filtered by public jobs only
        """
        return qs.filter(private=False)

    @classmethod
    def compas_job_filter(cls, queryset, info):
        """
        Used by CompasJobNode to filter which jobs are visible to the requesting user.

        A user must be logged in to view any compas jobs
        A user who is not a ligo user can not view ligo jobs

        :param queryset: The CompasJobNode queryset
        :param info: The CompasJobNode queryset info object
        :return: queryset filtered by ligo jobs if required
        """
        if info.context.user.is_anonymous:
            raise Exception("You must be logged in to perform this action.")

        # Users may not view ligo jobs if they are not a ligo user
        # if info.context.user.is_ligo:
        #     return queryset
        # else:
        #     return queryset.exclude(is_ligo_job=True)

        return queryset


class BasicParameter(models.Model):
    job = models.ForeignKey(CompasJob, related_name='basic_parameter', on_delete=models.CASCADE)

    name = models.CharField(max_length=55, blank=False, null=False)
    value = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {} ({})'.format(self.name, self.value, self.job)


class AdvancedParameter(models.Model):
    job = models.ForeignKey(CompasJob, related_name='advanced_parameter', on_delete=models.CASCADE)

    name = models.CharField(max_length=55, blank=False, null=False)
    value = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {} ({})'.format(self.name, self.value, self.job)


class SingleBinaryJob(models.Model):

    # required input parameters
    # --initial-mass-1
    mass1 = models.FloatField(
        blank=False,
        null=False,
        default=35.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(150.0)],
        help_text="Mass of the initially more massive star.  0 < Value < 150",
    )
    # --initial-mass-2
    mass2 = models.FloatField(
        blank=False,
        null=False,
        default=31.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(150.0)],
        help_text="Mass of the initially less massive star. 0 < Value < 150",
    )
    # --metalicity
    metallicity = models.FloatField(
        blank=False,
        null=False,
        default=0.001,
        validators=[MinValueValidator(1e-4), MaxValueValidator(0.03)],
        help_text="Metallicity of stars.  1E-4 < Value < 0.03",
    )
    # --eccentricity
    eccentricity = models.FloatField(
        blank=False,
        null=False,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1)],
        help_text="Orbital eccentricity of the binary. 0 <= Value < 1",
    )
    # --semi_major_axis
    separation = models.FloatField(
        blank=True,
        null=True,
        default=1.02,
        validators=[MinValueValidator(0.0)],
        help_text="Value > 0",
    )
    # --orbital_period
    orbital_period = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        help_text="Value > 0",
    )

    # --kick-magnitude-random-1
    velocity_random_number_1 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="--kick-magnitude-random-1: Value to be used to draw the \
        kick magnitude for the primary star of a binary system when evolving in BSE mode,\
        should the star undergo a supernova event, 0 < Value < 1",
    )
    # --kick-magnitude-random-2
    velocity_random_number_2 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="--kick-magnitude-random-2: Value to be used to draw the kick \
        magnitude for the secondary star of a binary system when evolving in BSE mode,\
         should the star undergo a supernova event, 0 < Value < 1",
    )
    # --kick-magnitude-1
    velocity_1 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=0.0,
        help_text="--kick-magnitude-1(Velocity1): Value to be used as the (drawn)\
         kick magnitude for the primary star of a binary system when evolving in\
          BSE mode, should the star undergo a supernova event (km s −1 ), Value > 0",
    )
    # --kick-magnitude-2
    velocity_2 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=0.0,
        help_text="--kick-magnitude-2(Velocity2): Value to be used as the (drawn)\
         kick magnitude for the secondary star of a binary system when evolving \
         in BSE mode, should the star undergo a supernova event (km s −1 ), Value > 0",
    )

    # --kick-theta-1
    theta_1 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-theta-1: The angle between the orbital plane and the ’z’ \
        axis of the supernova vector for the for the primary star of a binary system\
        when evolving in BSE mode, should it undergo a supernova event (radians), \
        0 < Value < 2pi",
    )
    # --kick-theta-2
    theta_2 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-theta-2: The angle between the orbital plane and the ’z’ axis\
         of the supernova vector for the for the secondary star of a binary system when\
          evolving in BSE mode, should it undergo a supernova event (radians), \
          0 < Value < 2pi",
    )
    # --kick-phi-1
    phi_1 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-phi-1: The angle between ’x’ and ’y’, both in the orbital \
        plane of the supernova vector, for the for the primary star of a binary system \
        when evolving in BSE mode, should it undergo a supernova event (radians), 0 < Value < 2pi",
    )
    # --kick-phi-2
    phi_2 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-phi-2: The angle between ’x’ and ’y’, both in the \
        orbital plane of the supernova vector, for the for the seocndary star \
        of a binary system when evolving in BSE mode, should it undergo a \
        supernova event (radians), 0 < Value < 2pi",
    )
    # --kick-mean-anomaly-1
    mean_anomaly_1 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-mean-anomaly-1: The mean anomaly at the instant of the \
        supernova for the primary star of a binary system when evolving in BSE mode, \
        should it undergo a supernova event, 0 < Value < 2pi",
    )
    # --kick-mean-anomaly-2
    mean_anomaly_2 = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0 * math.pi)],
        help_text="--kick-mean-anomaly-2: The mean anomaly at the instant of the supernova \
        for the secondary star of a binary system when evolving in BSE mode, should it \
        undergo a supernova event, 0 < Value < 2pi",
    )

    # common envelope
    # --common-envelope-alpha
    common_envelope_alpha = models.FloatField(
        blank=True,
        null=True,
        default=1.0,
        validators=[MinValueValidator(0.0)],
        help_text="--common-envelope-alpha: Common Envelope efficiency alpha, Value > 0",
    )
    # --common-envelope-lambda-prescription
    common_envelope_lambda_prescription = models.CharField(
        choices=constants.COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.COMMON_ENVELOPE_LAMBDA_PRESCRIPTION_NANJING_VALUE,
        help_text="--common-envelope-lambda-prescription: CE lambda prescription",
    )
    # --common-envelope-lambda
    common_envelope_lambda = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=0.1,
        help_text="--common-envelope-lambda: Common Envelope lambda, Value > 0",
    )

    # supernova
    # --remnant-mass-prescription
    remnant_mass_prescription = models.CharField(
        choices=constants.REMNANT_MASS_PRESCRIPTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.REMNANT_MASS_PRESCRIPTION_FRYER2012_VALUE,
        help_text="--remnant-mass-prescription: Remnant mass prescription",
    )
    # --fryer-supernova-engine
    fryer_supernova_engine = models.CharField(
        choices=constants.FRYER_SUPERNOVA_ENGINE_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.FRYER_SUPERNOVA_ENGINE_DELAYED_VALUE,
        help_text="--fryer-supernova-engine: Supernova engine type if using \
        the fallback prescription from Fryer et al. (2012)",
    )
    # --black-hole-kicks
    black_hole_kicks = models.CharField(
        choices=constants.BLACK_HOLE_KICKS_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.BLACK_HOLE_KICKS_FALLBACK_VALUE,
        help_text="--black-hole-kicks: Black hole kicks relative to NS kicks",
    )
    # --kick-magnitude-distribution
    kick_velocity_distribution = models.CharField(
        choices=constants.KICK_VELOCITY_DISTRIBUTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.KICK_VELOCITY_DISTRIBUTION_MAXWELLIAN,
        help_text="--kick-magnitude-distribution: Natal kick magnitude distribution",
    )
    # --kick-magnitude-sigma-CCSN-NS
    kick_velocity_sigma_CCSN_NS = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=250.0,
        help_text="--kick-magnitude-sigma-CCSN-NS: Sigma for chosen kick magnitude \
        distribution for neutron stars (km s − 1 ), Value > 0",
    )
    # --kick-magnitude-sigma-CCSN-BH
    kick_velocity_sigma_CCSN_BH = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=256.0,
        help_text="--kick-magnitude-sigma-CCSN-BH: Sigma for chosen kick magnitude \
        distribution for black holes (km s − 1 ), Value > 0",
    )
    # --kick-magnitude-sigma-ECSN
    kick_velocity_sigma_ECSN = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=30.0,
        help_text="--kick-magnitude-sigma-ECSN: Sigma for chosen kick magnitude \
        distribution for ECSN (km s − 1 ), Value > 0",
    )
    # --kick-magnitude-sigma-USSN
    kick_velocity_sigma_USSN = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=30.0,
        help_text="--kick-magnitude-sigma-USSN: Sigma for chosen kick magnitude \
        distribution for USSN (km s − 1 ), Value > 0",
    )

    # --pair-instability-supernovae
    pair_instability_supernovae = models.BooleanField(
        blank=True,
        null=True,
        help_text="--pair-instability-supernovae: Enable pair instability supernovae (PISN)"
    )

    # --pisn-lower-limit
    pisn_lower_limit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=60.0,
        help_text="--pisn-lower-limit: Minimum core mass for PISN, Value > 0",
    )
    # --pisn-upper-limit
    pisn_upper_limit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=135.0,
        help_text="--pisn-upper-limit: Maximum core mass for PISN, \
        0 < Value >  --pisn-lower-limit",
    )
    # --pulsational-pair-instability
    pulsational_pair_instability_supernovae = models.BooleanField(
        null=True,
        blank=True,
        help_text="--pulsational-pair-instability: Enable mass loss due to \
        pulsational-pair-instability (PPI)",
    )

    # --pisn-lower-limit
    ppi_lower_limit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=35.0,
        help_text="--pisn-lower-limit: Minimum core mass for PPI, Value > 0",
    )
    # --pisn-upper-limit
    ppi_upper_limit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=60.0,
        help_text="--pisn-upper-limit: Maximum core mass for PPI, \
        0 < Value > --pisn-lower-limit",
    )
    # --pulsational-pair-instability-prescription
    pulsational_pair_instability_prescription = models.CharField(
        choices=constants.PULSATIONAL_PAIR_INSTABILITY_PRESCRIPTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.PULSATIONAL_PAIR_INSTABILITY_PRESCRIPTION_MARCHANT,
        help_text="--pulsational-pair-instability-prescription: \
        Pulsational pair instability prescription",
    )
    # --maximum-neutron-star-mass
    maximum_neutron_star_mass = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=3.0,
        help_text="--maximum-neutron-star-mass: Maximum mass of a neutron star, Value > 0",
    )

    # Mass transfer
    # --mass-transfer-angular-momentum-loss-prescription
    mass_transfer_angular_momentum_loss_prescription = models.CharField(
        choices=constants.MASS_TRANSFER_ANGULAR_MOMENTUM_LOSS_PRESCRIPTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.MASS_TRANSFER_ANGULAR_MOMENTUM_LOSS_PRESCRIPTION_ISOTROPIC_VALUE,
        help_text="--mass-transfer-angular-momentum-loss-prescription: \
        Mass Transfer Angular Momentum Loss prescription",
    )
    # --mass-transfer-accretion-efficiency-prescription
    mass_transfer_accretion_efficiency_prescription = models.CharField(
        choices=constants.MASS_TRANSFER_ACCRETION_EFFICIENCY_PRESCRIPTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.MASS_TRANSFER_ACCRETION_EFFICIENCY_PRESCRIPTION_THERMAL_VALUE,
        help_text="--mass-transfer-accretion-efficiency-prescription: \
        Mass transfer accretion efficiency prescription",
    )
    # Ideally should only appear if using --mass-transfer-accretion-efficiency-prescription FIXED
    # --mass-transfer-fa
    mass_transfer_fa = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=0.5,
        help_text='--mass-transfer-fa: Mass Transfer fraction accreted \
        in FIXED prescription',
    )
    # Ideally should only appear if using --mass-transfer-angular-momentum-loss-prescription ARBITRARY
    # --mass-transfer-jloss
    mass_transfer_jloss = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        default=1.0,
        help_text='--mass-transfer-jloss: Specific angular \
        momentum with which the non-accreted system leaves the system',
    )

    def save(self, *args, **kwargs):
        """
        overwrites default save model behavior
        """
        super().save(*args, **kwargs)
        self.save_BSE_Grid_file()

    def save_BSE_Grid_file(self):
        """
        saves initial parameters and advanced settings in BSE_grid.txt file to filesystem
        """
        content = ""

        for field in self._meta.get_fields():

            field_value = getattr(self, field.name)
            if (field_value is not None) and (field.name in constants.FIELD_COMMANDS):
                content += f'{constants.FIELD_COMMANDS[field.name]} {field_value}' + " "

        # path where the file is saved: media_root/job_key
        storage_location = Path(settings.COMPAS_IO_PATH).joinpath(str(self.id))

        # create directory
        if not os.path.exists(storage_location):
            os.makedirs(
                storage_location,
            )
        # name parameter file
        grid_file_path = Path(storage_location).joinpath('BSE_grid.txt')

        # write parameters string to file
        with open(grid_file_path, 'w') as f:
            f.write(content)
