import logging
from django.core.management import BaseCommand
from django.db.models import Count
import sys
from soviet.consts import JOB_STATUS_FAILED, JOB_STATUS_UNSTARTED, \
    JOB_STATUS_COMPLETE, JOB_STATUS_NAMES
from soviet.job_management import run_all_jobs
from random import randint
from soviet.models import Job
from soviet import make_job, get_total_progress_percentage, run_job_slaves


class StreamWrapper(object):
    def __init__(self, out_file):
        self.out_file = out_file

    def __getattr__(self, key):
        return getattr(self.out_file, key)

    def write(self, str):
        self.out_file.write(str)
        self.out_file.flush()


class SovietManagementCommands(object):
    def job_slave(self, args, options):
        slave_id = args.pop(0)

        try:
            log_name = args.pop(0)
        except:
            log_name = None
        if log_name:
            sys.stdout = sys.stderr = StreamWrapper(file(log_name, "wb"))
        if options.get("verbosity") >= 2:
            logging.basicConfig(level=logging.INFO)
        run_all_jobs(slave_id=slave_id)

    def restart_errors(self, args, options):
        n_updated = Job.objects.filter(status=JOB_STATUS_FAILED).\
            update(status=JOB_STATUS_UNSTARTED)
        print "%d jobs restarted" % n_updated

    def test(self, args, options):
        print "Creating jobs"

        for x in xrange(500):
            r = randint(0, 100)
            if r < 33:
                make_job(
                    "soviet.menial_jobs:calculate_sum",
                    {"a": randint(100, 5000), "b": randint(-100, 2500)}
                )
            elif r < 66:
                make_job(
                    "soviet.menial_jobs:calculate_power",
                    {"a": randint(12, 500), "b": randint(12, 500)}
                )
            else:
                make_job(
                    "soviet.menial_jobs:slow_job",
                    {"delay": randint(100, 5000) / 1000.0}
                )
        print "Spinning up workers..."
        print run_job_slaves(10, delay=0, log_basename="test-worker-", verbose=True)

    def purge_errors(self, args, options):
        Job.objects.filter(status=JOB_STATUS_FAILED).delete()
        print "Jobs purged"

    def purge_completed(self, args, options):
        Job.objects.filter(status=JOB_STATUS_COMPLETE).delete()
        print "Jobs purged"

    def status(self, args, options):
        statuses = dict(Job.objects.values("status").annotate(n=Count("status")).\
            values_list("status", "n"))
        for status, name in sorted(JOB_STATUS_NAMES.iteritems()):
            if statuses.get(status):
                print "%15s : %5d" % (name, statuses.get(status))
        print "Total progress: %.3f%%" % get_total_progress_percentage()

    def help(self, args, options):
        print "Commands:"
        print "  job_slave       - run all jobs in queue"
        print "  test            - create menial jobs, then run them"
        print "  restart_errors  - restart errored-out jobs"
        print "  purge_errors    - purge errored-out jobs"
        print "  purge_completed - purge completed jobs"
        print "  status          - print some job queue statistics"


class Command(BaseCommand):
    help = "Manage the Soviet job management system."
    args = "<command> [arguments...]"

    def handle(self, command="help", *args, **options):
        args = list(args)
        management_commands = SovietManagementCommands()
        func = getattr(management_commands, command, None)
        if func and callable(func):
            func(args, options)
        else:
            print "Unknown command %r." % command
