import datetime
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from .utils import constants
from .utils.jobs.request_file_download_id import request_file_download_id
from .utils.jobs.request_file_list import request_file_list
from .utils.jobs.request_job_status import request_job_status


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

    @classmethod
    def get_by_name(cls, user, name):
        """
        Get CompasJob by the provided id

        This function will raise an exception if:-
        * the job requested is a ligo job, but the user is not a ligo user
        * the job requested is private an not owned by the requesting user

        :param user: The GWCloudUser instance making the request
        :param name: job name to be looked up
        :return: CompasJob
        """

        qs = cls.objects.filter(name__exact=name, user_id__exact=user.user_id)
        job = None if qs.count() == 0 else qs[0]

        return job


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


class FileDownloadToken(models.Model):
    """
    Copied from GWLab - This model tracks files from job file lists which can be used to generate file download tokens
    from the job controller
    """
    job = models.ForeignKey(CompasJob, on_delete=models.CASCADE, db_index=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4, db_index=True)
    path = models.TextField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def prune(cls):
        """
        Removes expired tokens from the database
        :return:
        """
        cls.objects.filter(
            created__lt=timezone.now() - datetime.timedelta(seconds=settings.FILE_DOWNLOAD_TOKEN_EXPIRY)
        ).delete()

    @classmethod
    def get_by_token(cls, token):
        cls.prune()
        tok = cls.objects.filter(token=token)
        if not tok.exists():
            return None
        return tok.first()

    @classmethod
    def create(cls, job, paths):
        """
        Creates a bulk number of FileDownloadToken objects for a specific job and list of paths, and returns the
        created objects
        """
        data = [cls(job=job, path=p) for p in paths]
        return cls.objects.bulk_create(data)

    @classmethod
    def get_paths(cls, job, tokens):
        """
        Returns a list of paths from a list of tokens, any token that isn't found will have a path of None
        The resulting list, will have identical size and ordering to the provided list of tokens
        """
        cls.prune()
        objects = {
            str(f.token): f.path for f in cls.objects.filter(job=job, token__in=tokens)
        }
        return [
            objects[str(tok)] if str(tok) in objects else None for tok in tokens
        ]


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

    # --kick-magnitude-distribution
    kick_velocity_distribution = models.CharField(
        choices=constants.KICK_VELOCITY_DISTRIBUTION_CHOICES,
        max_length=55,
        blank=True,
        null=True,
        default=constants.KICK_VELOCITY_DISTRIBUTION_MAXWELLIAN,
        help_text="--kick-magnitude-distribution: Natal kick magnitude distribution",
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

    def save(self, *args, **kwargs):
        """
        overwrites default save model behavior
        """
        super().save(*args, **kwargs)
        # self.save_BSE_Grid_file()

    def save_BSE_Grid_file(self):
        """
        saves initial parameters and advanced settings in BSE_grid.txt file to filesystem
        """
        content = ""

        for field in self._meta.get_fields():

            field_value = getattr(self, field.name)
            if (field_value is not None) and (field.name in constants.SINGLE_BINARY_FIELD_COMMANDS):
                content += f'{constants.SINGLE_BINARY_FIELD_COMMANDS[field.name]} {field_value} '

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
