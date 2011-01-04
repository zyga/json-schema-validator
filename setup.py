#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of linaro-json. 
#
# linaro-json is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# linaro-json is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with linaro-json.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

try:
    # This can fail when install_requires is not yet available and we
    # want to parse setup() to get to that list. During that time it's
    # not really important to know the precise version, we will know it
    # later once the deps are in place
    from linaro_json import __version__
except ImportError as ex:
    __version__ = "unknown"


setup(
    name = 'linaro-json',
    version = str(__version__),
    author = "Zygmunt Krynicki",
    author_email = "zygmunt.krynicki@linaro.org",
    description = "JSON manipulation utilities developed by the Linaro infrastructure team",
    packages = ['linaro_json',
                'linaro_json.proxies',
                'linaro_json.tests'],
    url='https://launchpad.net/linaro-python-json',
    test_suite='linaro_json.tests.test_suite',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
    ],
    install_requires = [
        'simplejson >= 2.0.9',
        'versiontools >= 1.0.2',
    ],
    setup_requires = [
        'versiontools >= 1.0.2',
    ],
    tests_require = [
        'testscenarios >= 0.2',
        'testtools >= 0.9.2',
    ],
    zip_safe = True,
)
