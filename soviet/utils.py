""" Some useful utilities for Soviet. """

from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib

# Try to import the best known JSON implementation.

try:
    from json import loads as load_json, dumps as dump_json
except ImportError:
    from django.utils.simplejson import loads as load_json, dumps as dump_json


def load(specification, context_explanation="Load"):
    """ Load an object from a module given a specification string.

    :param specification: Spec string, of the format ``module:name``.
    :param context_explanation: A context explanation, for more helpful exceptions.
    """
    module_name, object_name = specification.split(":", 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError, ie:
        raise ImproperlyConfigured(
            u"%s: Could not import module %r to load %r from. (%r)" %
            (context_explanation, module_name, object_name, ie))
    obj = getattr(module, object_name, None)
    if obj is None:
        raise ImproperlyConfigured(
            u"%s: Module %r does not have a name %r, or its value is None." %
            (context_explanation, module, object_name)
        )
    return obj
