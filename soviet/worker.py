""" Worker-y things. """
from soviet.consts import JOB_STATUS_COMPLETE, JOB_STATUS_RUNNING, \
    JOB_STATUS_FAILED, JOB_STATUS_STARTED
from soviet.utils import load, load_json
from os import getpid
from soviet.models import JobError
import datetime
import logging
import traceback

getid = id

log = logging.getLogger("soviet.worker")


class Worker(object):
    """ The Worker class, hero of the state. """

    def __init__(self, job, id=None):
        """
        :type job: soviet.models.Job
        :param job: The job to run.
        :param id: An optional identification string.
        """
        if not id:
            id = "%08d-%016x" % (getpid(), getid(self))
        self.id = unicode(id)
        self.job = job

    def run(self, propagate_exception=False):
        """ Main entry point for running a Job.

        This function is probably not called by client code,
        but by "run_job".
        """
        try:
            assert (self.job.status == JOB_STATUS_STARTED), "Job is in strange state."
            self._begin()
            self._run()
            log.info("(%s) job %s complete" % (self.id, self.job.pk))
            return True
        except:
            self._fail(traceback.format_exc())
            if propagate_exception:
                raise
            else:
                return False

    def _run(self):
        """ The actual method to load and fire some code according to spec. """
        callable = load(self.job.spec)
        kwargs = load_json(self.job.kwargs or {})
        reports_progress = getattr(callable, "reports_progress", False)
        if reports_progress:
            retval = callable(self.job.report_progress, **kwargs)
        else:
            retval = callable(**kwargs)
        self._complete(retval)

    def _complete(self, retval):
        """ Called when a job completes successfully. """
        if retval is not None:
            self.job.return_value = unicode(retval)
        else:
            self.job.return_value = None

        self.job.progress_value = 100
        self.job.progress_text = ""
        self.job.status = JOB_STATUS_COMPLETE
        self.job.finished_on = datetime.datetime.now()
        self.job.save()

    def _begin(self):
        """ Called when a job is started, just before _run(). """
        self.job.worker = self.id
        self.job.status = JOB_STATUS_RUNNING
        self.job.started_on = datetime.datetime.now()
        log.info("(%s) job %s starting" % (self.id, self.job.pk))
        self.job.save()

    def _fail(self, exception_text):
        """ Called when a job miserably fails. Records the error. """
        JobError.objects.create(
            job=self.job,
            worker=self.id,
            exception_text=exception_text
        )
        log.info("(%s) job %s failed" % (self.id, self.job.pk))
        self.job.status = JOB_STATUS_FAILED
        self.job.finished_on = datetime.datetime.now()
        self.job.save()
