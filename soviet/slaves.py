""" Slave process management. Shouldn't be needed by client code. """

import sys
import time
import uuid
from django.conf import settings
import os
import subprocess


def find_manage_py():
    """ Attempt to find 'manage.py', either via Django's settings,
    or by probing around the file system.
    """
    manage_py = getattr(settings, "SOVIET_MANAGE_PY", None)
    if manage_py and os.path.isfile(manage_py):
        return manage_py

    try:
        settings_module = __import__(os.environ["DJANGO_SETTINGS_MODULE"])
        settings_file = settings_module.__file__
    except:
        settings_file = None

    possible_bases = [
        os.path.dirname(settings_file) if settings_file else None,
        os.path.dirname(__file__)
    ]
    for base_dir in possible_bases:
        dirname = base_dir
        for x in xrange(4):
            pathname = os.path.abspath(os.path.join(dirname, "manage.py"))
            if os.path.isfile(pathname):
                return pathname
            else:
                dirname = os.path.join(dirname, "..")


def run_job_slaves(slaves_to_run=1, delay=0.2, log_basename=None, verbose=False):
    """ Start a given number of job slave processes.

    :param slaves_to_run: The number of slaves to run.
    :param delay: Delay (in seconds) to wait between each invocation.
    :param log_basename: The basename for log files for the workers.
                         For instance, ``log_basename="/tmp/foo-"`` would generate
                         log files of the form ``/tmp/foo-WORKERIDHERE.log``.
    :return: Returns a list of PIDs of the slaves spawned.
    """
    pids = []
    manage_py = find_manage_py()
    if not manage_py:
        raise ValueError("Soviet couldn't find your manage.py --"
                         "please manually define it in settings "
                         "(SOVIET_MANAGE_PY)")

    args = [
        sys.executable, manage_py,
        ("-v2" if verbose else "-v0"),
        "soviet_manage", "job_slave"
    ]

    for x in xrange(slaves_to_run):
        slave_id = uuid.uuid4().hex
        sl_args = args + [slave_id]
        if log_basename:
            sl_args.append("%s%s.log" % (log_basename, slave_id))
        pids.append(subprocess.Popen(sl_args).pid)
        time.sleep(delay)
    return pids
