""" Job management functions. Shouldn't usually be necessary for client code to call. """
from django.db import transaction
from itertools import count
from soviet.consts import JOB_STATUS_UNSTARTED, JOB_STATUS_STARTED
from soviet.models import Job
from soviet.worker import Worker
import time


def get_and_lock_next_job():
    """
    Attempt to atomically get a job to run from the data store.
    This expects select_for_update() to work in a sane way in
    the underlying database.
    """
    with transaction.commit_on_success():
        try:
            job = Job.objects.filter(status=JOB_STATUS_UNSTARTED).\
                  select_for_update()[:1][0]
        except IndexError:
            return None
        else:
            job.status = JOB_STATUS_STARTED
            job.save()
            return job


def run_job(job, id=None, propagate_exception=False):
    """ Spawn a Worker to run the given job, then run it.

    :param job: The job to run.
    :type job: soviet.models.Job
    :param id: The optional worker identification to give the worker.
               A pseudorandom identifier is used if omitted.
    :param propagate_exception: Propagate (re-raise) exceptions from
                                the worker instead of just saving the
                                worker status.
    :return: (job, status) tuple
    """
    worker = Worker(job, id=id)
    return (job, worker.run(propagate_exception=propagate_exception))


def run_next_job(id=None, propagate_exception=False):
    """ Run a job from the queue.

    :param id: The optional worker identification to give the worker.
               A pseudorandom identifier is used if omitted.
    :param propagate_exception: Propagate (re-raise) exceptions from
                                the worker instead of just saving the
                                worker status.
    :return: (job?, status?) tuple
    """
    job = get_and_lock_next_job()
    if job:
        return run_job(job, id, propagate_exception=propagate_exception)
    else:
        return (None, None)


def run_all_jobs(slave_id=None, delay=0.1):
    """ Run jobs from the queue until it's exhausted.
    :param slave_id: The optional worker identification to
                     give the worker. A pseudorandom identifier
                     is used if omitted.
    :param delay: Delay (in seconds) between execution of jobs.
    """
    for n in count(1):
        if slave_id:
            id = "%s:%s" % (slave_id, n)
        else:
            id = None

        job, result = run_next_job(id=id)
        if job is None:
            break
        time.sleep(delay)
