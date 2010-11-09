# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of Launch Control.
#
# Launch Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# Launch Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Launch Control.  If not, see <http://www.gnu.org/licenses/>.

"""
Package with unit tests for launch_control
"""

import doctest
import testscenarios
import unittest

def app_modules():
    return [
            'linaro_json',
            'linaro_json.decoder',
            'linaro_json.encoder',
            'linaro_json.impl',
            'linaro_json.interface',
            'linaro_json.pod',
            'linaro_json.proxies',
            'linaro_json.proxies.datetime_proxy',
            'linaro_json.proxies.decimal_proxy',
            'linaro_json.proxies.timedelta_proxy',
            'linaro_json.proxies.uuid_proxy',
            'linaro_json.proxy_registry',
            'linaro_json.schema',
            ]


def test_modules():
    return [
            'linaro_json.tests.test_schema',
            'linaro_json.tests.test_utils_json_package',
            ]


def test_suite():
    """
    Build an unittest.TestSuite() object with all the tests in _modules.
    Each module is harvested for both regular unittests and doctests
    """
    modules = app_modules() + test_modules()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in modules:
        unit_suite = loader.loadTestsFromName(name)
        suite.addTests(testscenarios.generate_scenarios(unit_suite))
        doc_suite = doctest.DocTestSuite(name)
        suite.addTests(doc_suite)
    return suite
