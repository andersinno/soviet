from distutils.core import setup

setup(
	name='Soviet',
    description="Simple job management for Django.",
	version='0.1',
	packages=[
        'soviet',
        'soviet.management',
        'soviet.management.commands',
    ],
	license='MIT',
	long_description=open('README.md').read(),
)