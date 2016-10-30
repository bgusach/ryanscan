# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


setup(
    name='ryanscanner',
    version='0.1.0',
    license='MIT',
    description='Tool to automate the search of Ryanair\'s flights',
    author='Bor González-Usach',
    author_email='bgusach@gmail.com',
    url='https://github.com/bgusach/ryanscanner',
    packages=find_packages(b'src'),
    package_dir={'': b'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'requests',
        'docopt',
    ],
    extras_require={
    },
    entry_points={
        'console_scripts': [
            'ryanscanner=ryanscanner.__main__:main',
        ]
    },
)

