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
Module with proxy type for uuid.UUID
"""

from uuid import UUID

from linaro_json.interface import ISimpleJSONType
from linaro_json.proxy_registry import DefaultClassRegistry


class UUIDProxy(ISimpleJSONType):

    def __init__(self, obj):
        self._obj = obj

    def to_json(self):
        return str(self._obj)

    @classmethod
    def from_json(self, json_str):
        if not isinstance(json_str, basestring):
            raise TypeError("Unable to decode UUID from a non-string")
        return UUID(json_str)


DefaultClassRegistry.register_proxy(UUID, UUIDProxy)
