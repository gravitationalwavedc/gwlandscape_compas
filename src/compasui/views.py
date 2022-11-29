from django.db import transaction

from .models import CompasJob, Label, SingleBinaryJob, BasicParameter
from .utils.jobs.submit_job import submit_job


def create_compas_job(user, start, basic_parameters):

    with transaction.atomic():
        compas_job = CompasJob(
            user_id=user.user_id,
            name=start.name,
            description=start.description,
            private=start.private,
            is_ligo_job=False
        )
        compas_job.save()

        for name, value in basic_parameters.items():
            BasicParameter(job=compas_job, name=name, value=value).save()

        # Submit the job to the job controller

        # Create the parameter json
        params = compas_job.as_json()

        # Save the job id
        compas_job.job_controller_id = submit_job(params, user.user_id)
        compas_job.save()
        return compas_job


def update_compas_job(job_id, user, private=None, labels=None):
    compas_job = CompasJob.get_by_id(job_id, user)

    if user.user_id == compas_job.user_id:
        if labels is not None:
            compas_job.labels.set(Label.filter_by_name(labels))

        if private is not None:
            compas_job.private = private

        compas_job.save()

        return 'Job saved!'
    else:
        raise Exception('You must own the job to change the privacy!')


def create_single_binary_job(user, **kwargs):
    single_binary_job = SingleBinaryJob(
        **kwargs
    )
    single_binary_job.save()

    params = single_binary_job.as_json()

    single_binary_job.job_controller_id = submit_job(params, user.user_id)
    single_binary_job.save()

    # model_id = str(single_binary_job.id)
    #
    # grid_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'BSE_grid.txt')
    # output_path = os.path.join(settings.COMPAS_IO_PATH, model_id)
    # detailed_output_file_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output',
    #                                          'Detailed_Output', 'BSE_Detailed_Output_0.h5')
    # detailed_plot_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output',
    #                                   'Detailed_Output', 'detailedEvolutionPlot.png')
    # vanDenHeuval_plot_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output',
    #                                       'Detailed_Output', 'vanDenHeuvalPlot.png')
    # evol_text_path = os.path.join(settings.COMPAS_IO_PATH, model_id, 'COMPAS_Output',
    #                               'Detailed_Output', 'detailed_evol.txt')
    #
    # task = chain(run_compas.s(grid_file_path, output_path, detailed_output_file_path),
    #              run_detailed_evol_plotting.s(detailed_output_file_path, detailed_plot_path,
    #                                           vanDenHeuval_plot_path, evol_text_path))()
    # # get task result
    # result = task.get()
    # if result in (TASK_FAIL, TASK_TIMEOUT):
    #     raise Exception(model_id)

    return single_binary_job
