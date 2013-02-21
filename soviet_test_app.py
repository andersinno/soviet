#!/usr/bin/env python

# This file is a terrible, terrible hack.
# I love it.

import os
import sys
import tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "__main__")

SOVIET_MANAGE_PY = os.path.abspath(__file__)
INSTALLED_APPS = ("soviet",)
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(tempfile.gettempdir(), "soviet_test.sqlite3"),
	}
}

if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)