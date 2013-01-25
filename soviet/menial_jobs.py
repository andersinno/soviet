""" Some menial test jobs used by soviet_manage test. """
import time


def calculate_sum(a, b):
    """ Sum two objects. """
    return (a + b)


def calculate_power(a, b):
    """ Calculate the power of two objects. """
    return a ** b


def slow_job(delay):
    """ Wait for a while. """
    print "Waiting for %s" % delay
    time.sleep(delay)
