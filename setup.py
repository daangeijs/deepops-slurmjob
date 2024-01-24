from setuptools import setup, find_packages


# Read requirements.txt and convert it to a list of requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    author='Daan Geijs',
    name='slurmjob',
    version='0.3.2',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'slurmjob=slurmjob.main:main',
        ],
    },
)