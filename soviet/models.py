""" Models for Soviet. """

from django.db import models
from soviet.consts import JOB_STATUS_NAMES


class Job(models.Model):
    """ A job to be run. """

    status = models.PositiveSmallIntegerField(default=0,
        db_index=True, choices=sorted(JOB_STATUS_NAMES.iteritems()))
    description = models.CharField(max_length=64, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(blank=True, null=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    worker = models.CharField(max_length=64, blank=True)
    spec = models.CharField(max_length=128)
    kwargs = models.TextField(blank=True)
    return_value = models.TextField(blank=True, null=True)
    progress_value = models.IntegerField(default=0)
    progress_text = models.CharField(max_length=128, blank=True)

    def report_progress(self, value, text=""):
        """ Report the progress of this job.
        This function is passed to any job callable that has the
        @reports_progress decoration.
        """
        self.progress_value = int(value)
        self.progress_text = text
        self.save()


class JobError(models.Model):
    """ An error recorded while executing a job. """
    job = models.ForeignKey(Job)
    created_on = models.DateTimeField(auto_now_add=True)
    exception_text = models.TextField()
    worker = models.CharField(max_length=64, blank=True)
