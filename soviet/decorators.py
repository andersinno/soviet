""" Decorator(s) for Soviet jobs. """


def reports_progress(func):
    """Decorate the given function to report progress.

    Progress-reporting functions receive
    :py:func:`soviet.models.Job.report_progress` as their first argument,
    that is, a function of the signature f(value, text=""). ``value`` is
    expected to be an integer between 0 and 100.
    """
    func.reports_progress = True
    return func
