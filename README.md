Soviet
======

Soviet is a Django app that's sorta-kinda Celery's little communist brother.

It lets your apps -- usually small, non-distributed apps -- easily do work in the background.
It's also proudly opinionated -- the only queue store available is Django's database.

The slave processes may be directly started after you've enqueued some jobs, or you might have
a cron job or similar to actually have some work done.

As usual, better documentation may eventually ensue.

What's with the name?
---------------------

Some whimsy and free association riffing on "workers", etc.

Quick start/tour/something
--------------------------

1. Add Soviet to your Django ``INSTALLED_APPS`` and ``syncdb``.
2. Open up ``manage.py shell``. Run something like

    from soviet import make_job, run_job_slaves
    make_job("soviet.menial_jobs:calculate_sum", {"a": 1000, "b": 2000})
    make_job("soviet.menial_jobs:calculate_sum", {"a": None, "b": []})
    run_job_slaves()

3. A subprocess should start and run through all jobs available (all two of them).
4. A stringified version of the return value of each job is saved into the database.
5. Close the shell and check ``manage.py soviet_manage status``. If all went right,
   you should see one completed and one failed job (as you can't sum None and a list).
6. Examine the database at your leisure for the results.
7. Use ``soviet_manage purge_errors`` and ``soviet_manage purge_completed`` to remove
   the two jobs.