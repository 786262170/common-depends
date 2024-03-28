#!/usr/bin/env python3
# coding=utf-8
"""setup wheel"""
from sys import version_info

from setuptools import find_packages, setup

VERSION = "1.0.2"
DESCRIPTION = "Utils - plato public libs"

if version_info < (3, 10, 0):
    raise SystemExit("Sorry! utils requires python 3.10.0 or later.")

setup(
    # Package metadata
    name="qt-common",
    description=DESCRIPTION,
    author="changye.yang ",
    author_email="changye.yang@iquantex.com",
    url="https://gitlab.iquantex.com/plato/plato-fin-model/qt-common",
    long_description=open("README.md", encoding="gbk").read(),
    long_description_content_type="text/markdown",
    # Versioning
    version=VERSION,
    license="BSD Licence",
    # Package setup
    packages=find_packages(include=[
        "common",
        "common.*",
    ]),
    include_package_data=True,
    # Requirements
    python_requires=">= 3.10.0",
    install_requires=[
        "loguru>=0.5.3", "sqlalchemy==1.4.41", "PyMySQL==1.0.2",
        "pandas==1.5.0", "numpy==1.23.3", "asgiref==3.5.2",
        "chinese-calendar==1.8.0"
    ],
    tests_require=[
        "pytest",
        "pytest-mock",
        "pytest-cover",
        "pytest-asyncio==0.20.3",
        "testfixtures",
    ],
    classifiers=[
        "Programming Language :: Python :: 3", "Framework :: Quant",
        "Intended Audience :: Developers",
        "License :: OSI Approved ::  License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10", "Topic :: Internet"
    ])
