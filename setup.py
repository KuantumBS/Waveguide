"""Install waveguide package."""

import io
import sys
from os import path

from setuptools import setup  # find_packages


import waveguide

root = path.abspath(path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(path.join(root, filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.md')


setup(
    name="waveguide",
    version=waveguide.__version__,
    author="John Garrett",
    author_email="garrettj403@gmail.com",
    description="Calculate the properties of rectangular waveguides",
    license="MIT",
    url="https://github.com/garrettj403/Waveguide/",
    # keywords=[],
    # packages=find_packages(),
    py_modules=['waveguide'],
    install_requires=[
        'numpy',
        'scipy',
    ],
    extras_require={
        'testing': ['pytest'],
        'examples': ['matplotlib',
                     'scikit-rf', ],
    },
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    project_urls={
        'Changelog': 'https://github.com/garrettj403/Waveguide/blob/master/CHANGES.md',
        'Issue Tracker': 'https://github.com/garrettj403/Waveguide/issues',
    },
    # scripts=[],
)
