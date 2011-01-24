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

"""
Unit tests for JSON extensions
"""

from testtools import TestCase
from datetime import datetime

from linaro_json.extensions import datetime_extension


class DatetimeExtensionTests(TestCase):


    reference_obj = datetime(2010, 12, 7, 23, 59, 58)
    reference_text = "2010-12-07T23:59:58Z"


    def test_datetime_to_json(self):
        text = datetime_extension.to_json(self.reference_obj)
        self.assertEqual(text, self.reference_text)

    def test_datetime_from_json(self):
        obj = datetime_extension.from_json(self.reference_text)
        self.assertEqual(obj, self.reference_obj)




