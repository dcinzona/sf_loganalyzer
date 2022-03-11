#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
from typing import List

import setuptools

packages = [
    p
    for p in setuptools.find_namespace_packages()
    if p.startswith("sfloganalyzer") and not p.startswith("sfloganalyzer.docs")
]

with open(os.path.join("sfloganalyzer", "version.txt"), "r") as version_file:
    version = version_file.read().strip()


def parse_requirements_file(requirements_file) -> List[str]:
    requirements = []
    for req in requirements_file.read().splitlines():
        # skip comments and hash lines
        if not (re.match(r"\s*#", req) or re.match(r"\s*--hash", req)):
            req = req.split(" ")[0]
            requirements.append(req)
    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements/prod.txt") as requirements_file:
    requirements = parse_requirements_file(requirements_file)

with open("requirements/dev.txt") as dev_requirements_file:
    dev_requirements = parse_requirements_file(dev_requirements_file)

setuptools.setup(
    name="sfloganalyzer",
    version=version,
    description="Salesforce log analysis utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gustavo Tandeciarz",
    author_email="",
    url="https://github.com/dcinzona/sf_loganalyzer",
    packages=packages,  # list(find_packages(["sfloganalyzer"], "sfloganalyzer")),
    package_dir={"sfloganalyzer": "sfloganalyzer"},
    scripts=["bin/sfla"],
    entry_points={
        "console_scripts": [
            "sfla=sfloganalyzer.cli.sfla:main",
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    tests_require=dev_requirements,
    data_files=[("requirements", ["requirements/prod.txt", "requirements/dev.txt"])],
    license="BSD license",
    zip_safe=False,
    keywords="sfloganalyzer",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    test_suite="sfloganalyzer.tests",
    python_requires=">=3.9.10",
)
