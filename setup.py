import io
import os
from setuptools import setup, find_packages


def local_file(*name):
    return os.path.join(
        os.path.dirname(__file__),
        *name)


def read(name, **kwargs):
    with io.open(
        name,
        encoding=kwargs.get("encoding", "utf8")
    ) as handle:
        return handle.read()


def read_version():
    "Read the `(version-string, version-info)` from `spor/version.py`."
    version_file = local_file('spor', 'version.py')
    local_vars = {}
    with open(version_file) as handle:
        exec(handle.read(), {}, local_vars)  # pylint: disable=exec-used
    return (local_vars['__version__'], local_vars['__version_info__'])


long_description = read(local_file('README.rst'), mode='rt')

setup(
    name='spor',
    version=read_version()[0],
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),

    author='Sixty North AS',
    author_email='austin@sixty-north.com',
    description='A system for anchoring metadata in external files to source code',
    license='MIT',
    keywords='',
    url='https://github.com/sixty-north/spor',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    platforms='any',
    include_package_data=True,
    install_requires=[
        'docopt_subcommands',
        'pyyaml'
    ],
    extras_require={
        'test': ['pytest', 'radish-bdd', 'tox'],
    },
    entry_points={
        'console_scripts': [
           'spor = spor.cli:main',
        ],
    },
    long_description=long_description,
)
