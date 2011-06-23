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

"""
One liners that make the code shorter
"""

import simplejson

from json_schema_validator.schema import Schema
from json_schema_validator.validator import Validator


def validate(schema_text, data_text):
    """
    Validate specified JSON text (data_text) with specified schema (schema
    text). Both are converted to JSON objects with :func:`simplesjon.loads`.

    :param schema_text:
        Text of the JSON schema to check against
    :type schema_text:
        :class:`str`
    :param data_text:
        Text of the JSON object to check
    :type data_text:
        :class:`str`
    :returns:
        Same as :meth:`json_schema_validator.validator.Validator.validate`
    :raises:
        Whatever may be raised by simplejson (in particular
        :class:`simplejson.decoder.JSONDecoderError`, a subclass of :class:`ValueError`)
    :raises:
        Whatever may be raised by
        :meth:`json_schema_validator.validator.Validator.validate`. In particular
        :class:`json_schema_validator.errors.ValidationError` and
        :class:`json_schema_validator.errors.SchemaError`


    """
    schema = Schema(simplejson.loads(schema_text))
    data = simplejson.loads(data_text)
    return Validator.validate(schema, data)
