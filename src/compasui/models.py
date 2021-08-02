from django.db import models

from compasui.utils.jobs.request_file_download_id import request_file_download_id
from compasui.utils.jobs.request_file_list import request_file_list
from compasui.utils.jobs.request_job_status import request_job_status
from .variables import compas_parameters


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
        # Get the data container type for this job
        data = {
            "type": self.data.data_choice,
            "source": self.data.source_dataset
        }

        # Iterate over the data parameters
        for d in self.data_parameter.all():
            data[d.name] = d.value

        # Get the search parameters
        search = {}
        for s in self.search_parameter.all():
            search[s.name] = s.value

        return dict(
            name=self.name,
            description=self.description,
            data=data,
            search=search
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
        if job.is_ligo_job and not user.is_ligo:
            raise Exception("Permission Denied")

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
        if info.context.user.is_ligo:
            return queryset
        else:
            return queryset.exclude(is_ligo_job=True)


class Data(models.Model):
    """
    Model to store Data Source Information
    """
    job = models.OneToOneField(CompasJob, related_name='data', on_delete=models.CASCADE)

    data_choice = models.CharField(
        max_length=55,
        choices=compas_parameters.DATA_SOURCES,
        default=compas_parameters.REAL_DATA[0]
    )

    source_dataset = models.CharField(
        max_length=2,
        choices=compas_parameters.SOURCE_DATASETS,
        default=compas_parameters.O1[0],
        null=True,
        blank=True
    )

    def __str__(self):
        return '{} ({})'.format(self.data_choice, self.job.name)

    def as_json(self):
        return dict(
            id=self.id,
            value=dict(
                job=self.job.id,
                choice=self.data_choice,
                source=self.source_dataset
            ),
        )


class DataParameter(models.Model):
    """
    Model to Store Data Parameters.
    Serves for Real and Simulated Data parameters.
    """
    job = models.ForeignKey(CompasJob, related_name='data_parameter', on_delete=models.CASCADE)
    data = models.ForeignKey(Data, related_name='parameter', on_delete=models.CASCADE)

    name = models.CharField(max_length=55, blank=False, null=False)
    value = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {} ({})'.format(self.name, self.value, self.data)


class Search(models.Model):
    """
    Search Container
    """
    job = models.OneToOneField(CompasJob, related_name='search', on_delete=models.CASCADE)


class SearchParameter(models.Model):
    """
    Model to Store Search Parameters.
    """
    job = models.ForeignKey(CompasJob, related_name='search_parameter', on_delete=models.CASCADE)
    search = models.ForeignKey(Search, related_name='parameter', on_delete=models.CASCADE)

    name = models.CharField(max_length=55, blank=False, null=False)
    value = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {} ({})'.format(self.name, self.value, self.search)

