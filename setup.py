#!/usr/bin/env python
#
# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of json-schema-validator.
#
# json-schema-validator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# json-schema-validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with json-schema-validator.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='json-schema-validator',
    version=":versiontools:json_schema_validator:__version__",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    description="JSON Schema Validator",
    packages=find_packages(),
    url='https://github.com/zyga/json-schema-validator',
    test_suite='json_schema_validator.tests.test_suite',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"],
    install_requires=[
        'simplejson >= 2.0.9'],
    setup_requires=[
        'versiontools >= 1.3.1'],
    tests_require=[
        'testscenarios >= 0.1',
        'testtools >= 0.9.2'],
    zip_safe=True)
