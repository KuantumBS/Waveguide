"""Install waveguide package."""

from setuptools import setup, find_packages
import io
import re
import sys
import os

# UTF-8 encoding sorunlarını çöz
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_version():
    with open('waveguide/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="waveguide",
    version=get_version(),
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
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
    ],
    project_urls={
        'Changelog': 'https://github.com/garrettj403/Waveguide/blob/master/CHANGES.md',
        'Issue Tracker': 'https://github.com/garrettj403/Waveguide/issues',
    },
    # scripts=[],
)
