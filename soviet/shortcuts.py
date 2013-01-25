""" Useful helper functions, akin to django.shortcuts. """

from django.db.models import Count, Sum
from soviet.models import Job
from soviet.utils import dump_json


def make_job(callable_spec, kwargs=None, description=""):
    """ Create a job from the given callable and keyword arguments.

    :param callable_spec: A callable specification for the function to call.
                          Syntax '<module>:<name>', i.e. to call this
                          function, callable_spec would be
                          "soviet.shortcuts:make_job".
    :param kwargs:        Keyword arguments, if any, to pass to the job, in a dict.
                          Note that the arguments must be JSON serializable.
    :param description:   Optional human-readable description of the job.
    :return: The newly created job.
    :rtype: soviet.models.Job
    """
    if ":" not in callable_spec:
        raise ValueError("Callable specification has no colon. Syntax: <module>:<name>.")

    return Job.objects.create(
        spec=callable_spec,
        kwargs=(dump_json(kwargs) if kwargs else ""),
        description=description
    )


def get_total_progress_percentage(**job_filter):
    """ Get the total progress of all jobs matching a given Django queryset filter.

    Example: get_total_progress_percentage(spec="myapp.mailer:send_mails")

    :return: A floating point number (probably between 0 and 100)
             representing the total progress.
    """
    qs = Job.objects.all()
    if job_filter:
        qs = qs.filter(**job_filter)
    info = qs.aggregate(n=Count("id"), progress=Sum("progress_value"))
    try:
        return (info["progress"] / (info["n"] * 100.0) * 100)
    except (KeyError, ValueError, ZeroDivisionError), exc:
        return 0
