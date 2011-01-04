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
Universal JSON utilities developed by Linaro
"""

from linaro_json.impl import json
from linaro_json.decoder import PluggableJSONDecoder
from linaro_json.encoder import PluggableJSONEncoder
from linaro_json.interface import (
    IComplexJSONType,
    IFundamentalJSONType,
    ISimpleJSONType,
)
from linaro_json.proxy_registry import (
    ClassRegistry,
    DefaultClassRegistry,
)
from linaro_json.pod import PlainOldData
from linaro_json.schema import (
    Schema,
    SchemaError,
    ValidationError,
    Validator,
)


__version__ = "1.2.2.final"
try:
    import versiontools
    __version__ = versiontools.Version(*__version__.split("."))
except ImportError:
    pass


def get_version():
    """
    Return a string representing the version of this package
    """
    return str(__version__)

