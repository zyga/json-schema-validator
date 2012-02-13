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
Helper module to work with raw JSON Schema
"""

import re

from json_schema_validator.errors import SchemaError
from json_schema_validator.misc import NUMERIC_TYPES


class Schema(object):
    """
    JSON schema object
    """

    def __init__(self, json_obj):
        """
        Initialize schema with JSON object

        .. note::
            JSON objects are just plain python dictionaries

        """
        if not isinstance(json_obj, dict):
            raise SchemaError("Schema definition must be a JSON object")
        self._schema = json_obj

    def __repr__(self):
        return "Schema({0!r})".format(self._schema)

    @property
    def type(self):
        """
        Return the 'type' property of this schema.

        The return value is always a list of correct JSON types.
        Correct JSON types are one of the pre-defined simple types or
        another schema object.

        List of built-in simple types:
        * 'string'
        * 'number'
        * 'integer'
        * 'boolean'
        * 'object'
        * 'array'
        * 'any' (default)
        """
        value = self._schema.get("type", "any")
        if not isinstance(value, (basestring, dict, list)):
            raise SchemaError(
                "type value {0!r} is not a simple type name, nested "
                "schema nor a list of those".format(value))
        if isinstance(value, list):
            type_list = value
            # Union types have to have at least two alternatives
            if len(type_list) < 2:
                raise SchemaError(
                    "union type {0!r} is too short".format(value))
        else:
            type_list = [value]
        seen = set()
        for js_type in type_list:
            if isinstance(js_type, dict):
                # no nested validation here
                pass
            elif isinstance(js_type, list):
                # no nested validation here
                pass
            else:
                if js_type in seen:
                    raise SchemaError(
                        ("type value {0!r} contains duplicate element"
                         " {1!r}").format(value, js_type))
                else:
                    seen.add(js_type)
                if js_type not in (
                    "string", "number", "integer", "boolean", "object",
                    "array", "null", "any"):
                    raise SchemaError(
                        "type value {0!r} is not a simple type "
                        "name".format(js_type))
        return value

    @property
    def properties(self):
        """
        The properties property contains schema for each property in a
        dictionary.

        The dictionary name is the property name. The dictionary value
        is the schema object itself.
        """
        value = self._schema.get("properties", {})
        if not isinstance(value, dict):
            raise SchemaError(
                "properties value {0!r} is not an object".format(value))
        return value

    @property
    def items(self):
        value = self._schema.get("items", {})
        if not isinstance(value, (list, dict)):
            raise SchemaError(
                "items value {0!r} is neither a list nor an object".
                format(value))
        return value

    @property
    def optional(self):
        value = self._schema.get("optional", False)
        if value is not False and value is not True:
            raise SchemaError(
                "optional value {0!r} is not a boolean".format(value))
        return value

    @property
    def additionalProperties(self):
        value = self._schema.get("additionalProperties", {})
        if not isinstance(value, dict) and value is not False:
            raise SchemaError(
                "additionalProperties value {0!r} is neither false nor"
                " an object".format(value))
        return value

    @property
    def requires(self):
        value = self._schema.get("requires", {})
        if not isinstance(value, (basestring, dict)):
            raise SchemaError(
                "requires value {0!r} is neither a string nor an"
                " object".format(value))
        return value

    @property
    def minimum(self):
        value = self._schema.get("minimum", None)
        if value is None:
            return
        if not isinstance(value, NUMERIC_TYPES):
            raise SchemaError(
                "minimum value {0!r} is not a numeric type".format(
                    value))
        return value

    @property
    def maximum(self):
        value = self._schema.get("maximum", None)
        if value is None:
            return
        if not isinstance(value, NUMERIC_TYPES):
            raise SchemaError(
                "maximum value {0!r} is not a numeric type".format(
                    value))
        return value

    @property
    def minimumCanEqual(self):
        if self.minimum is None:
            raise SchemaError("minimumCanEqual requires presence of minimum")
        value = self._schema.get("minimumCanEqual", True)
        if value is not True and value is not False:
            raise SchemaError(
                "minimumCanEqual value {0!r} is not a boolean".format(
                    value))
        return value

    @property
    def maximumCanEqual(self):
        if self.maximum is None:
            raise SchemaError("maximumCanEqual requires presence of maximum")
        value = self._schema.get("maximumCanEqual", True)
        if value is not True and value is not False:
            raise SchemaError(
                "maximumCanEqual value {0!r} is not a boolean".format(
                    value))
        return value

    @property
    def minItems(self):
        value = self._schema.get("minItems", 0)
        if not isinstance(value, int):
            raise SchemaError(
                "minItems value {0!r} is not an integer".format(value))
        if value < 0:
            raise SchemaError(
                "minItems value {0!r} cannot be negative".format(value))
        return value

    @property
    def maxItems(self):
        value = self._schema.get("maxItems", None)
        if value is None:
            return
        if not isinstance(value, int):
            raise SchemaError(
                "maxItems value {0!r} is not an integer".format(value))
        return value

    @property
    def uniqueItems(self):
        value = self._schema.get("uniqueItems", False)
        if value is not True and value is not False:
            raise SchemaError(
                "uniqueItems value {0!r} is not a boolean".format(value))
        return value

    @property
    def pattern(self):
        """
        .. note::
            JSON schema specifications says that this value SHOULD
            follow the ``EMCA 262/Perl 5`` format. We cannot support
            this so we support python regular expressions instead. This
            is still valid but should be noted for clarity.


        :returns None or compiled regular expression
        """
        value = self._schema.get("pattern", None)
        if value is None:
            return
        try:
            return re.compile(value)
        except re.error as ex:
            raise SchemaError(
                "pattern value {0!r} is not a valid regular expression:"
                " {1}".format(value, str(ex)))

    @property
    def minLength(self):
        value = self._schema.get("minLength", 0)
        if not isinstance(value, int):
            raise SchemaError(
                "minLength value {0!r} is not an integer".format(value))
        if value < 0:
            raise SchemaError(
                "minLength value {0!r} cannot be negative".format(value))
        return value

    @property
    def maxLength(self):
        value = self._schema.get("maxLength", None)
        if value is None:
            return
        if not isinstance(value, int):
            raise SchemaError(
                "maxLength value {0!r} is not an integer".format(value))
        return value

    @property
    def enum(self):
        """
        Enumeration of possible correct values.

        *Must* be either ``None`` or a non-empty list of valid objects.
        The list *must not* contain duplicate elements.
        """
        value = self._schema.get("enum", None)
        if value is None:
            return
        if not isinstance(value, list):
            raise SchemaError(
                "enum value {0!r} is not a list".format(value))
        if len(value) == 0:
            raise SchemaError(
                "enum value {0!r} does not contain any"
                " elements".format(value))
        seen = set()
        for item in value:
            if item in seen:
                raise SchemaError(
                    "enum value {0!r} contains duplicate element"
                    " {1!r}".format(value, item))
            else:
                seen.add(item)
        return value

    @property
    def title(self):
        value = self._schema.get("title", None)
        if value is None:
            return
        if not isinstance(value, basestring):
            raise SchemaError(
                "title value {0!r} is not a string".format(value))
        return value

    @property
    def description(self):
        value = self._schema.get("description", None)
        if value is None:
            return
        if not isinstance(value, basestring):
            raise SchemaError(
                "description value {0!r} is not a string".format(value))
        return value

    @property
    def format(self):
        value = self._schema.get("format", None)
        if value is None:
            return
        if not isinstance(value, basestring):
            raise SchemaError(
                "format value {0!r} is not a string".format(value))
        if value in [
            'date-time',
            'regex',
        ]:
            return value
        raise NotImplementedError(
            "format value {0!r} is not supported".format(value))

    @property
    def contentEncoding(self):
        value = self._schema.get("contentEncoding", None)
        if value is None:
            return
        if value.lower() not in [
            "7bit", "8bit", "binary", "quoted-printable", "base64",
            "ietf-token", "x-token"]:
            raise SchemaError(
                "contentEncoding value {0!r} is not"
                " valid".format(value))
        if value.lower() != "base64":
            raise NotImplementedError(
                "contentEncoding value {0!r} is not supported".format(
                    value))
        return value

    @property
    def divisibleBy(self):
        value = self._schema.get("divisibleBy", 1)
        if value is None:
            return
        if not isinstance(value, NUMERIC_TYPES):
            raise SchemaError(
                "divisibleBy value {0!r} is not a numeric type".
                format(value))
        if value < 0:
            raise SchemaError(
                "divisibleBy value {0!r} cannot be"
                " negative".format(value))
        return value

    @property
    def disallow(self):
        value = self._schema.get("disallow", None)
        if value is None:
            return
        if not isinstance(value, (basestring, dict, list)):
            raise SchemaError(
                "disallow value {0!r} is not a simple type name, nested "
                "schema nor a list of those".format(value))
        if isinstance(value, list):
            disallow_list = value
        else:
            disallow_list = [value]
        seen = set()
        for js_disallow in disallow_list:
            if isinstance(js_disallow, dict):
                # no nested validation here
                pass
            else:
                if js_disallow in seen:
                    raise SchemaError(
                        "disallow value {0!r} contains duplicate element"
                        " {1!r}".format(value, js_disallow))
                else:
                    seen.add(js_disallow)
                if js_disallow not in (
                    "string", "number", "integer", "boolean", "object",
                    "array", "null", "any"):
                    raise SchemaError(
                        "disallow value {0!r} is not a simple type"
                        " name".format(js_disallow))
        return disallow_list

    @property
    def extends(self):
        raise NotImplementedError("extends property is not supported")

    @property
    def default(self):
        try:
            return self._schema["default"]
        except KeyError:
            raise SchemaError("There is no schema default for this item")
