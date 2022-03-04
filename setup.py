#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
from pkgutil import walk_packages

from setuptools import setup


def find_packages(path=["."], prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


with open(os.path.join("sfloganalyzer", "version.txt"), "r") as version_file:
    version = version_file.read().strip()

with open("README.rst", "rb") as readme_file:
    readme = readme_file.read().decode("utf-8")

with open("HISTORY.rst", "rb") as history_file:
    history = history_file.read().decode("utf-8")

with open("requirements/prod.txt") as requirements_file:
    requirements = []
    for req in requirements_file.read().splitlines():
        # skip comments and hash lines
        if re.match(r"\s*#", req) or re.match(r"\s*--hash", req):
            continue
        else:
            req = req.split(" ")[0]
            requirements.append(req)

setup(
    name="sfloganalyzer",
    version=version,
    description="Salesforce log analysis utility",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    author="Gustavo Tandeciarz",
    author_email="",
    url="https://github.com/dcinzona/sf_loganalyzer",
    packages=list(find_packages(["sfloganalyzer"], "sfloganalyzer")),
    package_dir={"sfloganalyzer": "sfloganalyzer"},
    entry_points={
        "console_scripts": [
            "sfla=sfloganalyzer.cli.sfla:main",
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords="sfloganalyzer",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    test_suite="sfloganalyzer.tests",
    python_requires=">=3.8",
)
