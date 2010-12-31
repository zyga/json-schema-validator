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
JSON schema validator for python

.. note::
    Only a subset of schema features are currently supported.
    Unsupported features are detected and raise a NotImplementedError
    when you call :func:`Validator.validate`

.. warning::
    This implementation was based on the *second draft* of the specification
    A third draft was published on the 22nd Nov 2010. This draft introduced
    several important changes that are not yet implemented.

.. seealso::
    http://json-schema.org/ for details about the schema
"""

import datetime
import decimal
import itertools
import re
import types

# Global configuration,
# List of types recognized as numeric
NUMERIC_TYPES = (int, float, decimal.Decimal)


class SchemaError(ValueError):
    """
    A bug in the schema prevents the program from working
    """


class ValidationError(ValueError):
    """
    A bug in the validated object prevents the program from working.

    The error instance has several interesting properties:

        :message:
            Old and verbose message that contains less helpful message
            and lots of JSON data (deprecated).
        :new_message:
            short and concise message about the problem
        :object_expr:
            A JavaScript expression that evaluates to the object that
            failed to validate. The expression always starts with a root
            object called ``'object'``.
        :schema_expr:
            A JavaScript expression that evaluates to the schema that was
            checked at the time validation failed. The expression always
            starts with a root object called ``'schema'``.

    """

    def __init__(self, message, new_message=None,
                 object_expr=None, schema_expr=None):
        self.message = message
        self.new_message = new_message
        self.object_expr = object_expr
        self.schema_expr = schema_expr

    def __str__(self):
        return ("ValidationError: {0} "
                "object_expr={1!r}, "
                "schema_expr={2!r})").format(
                    self.new_message, self.object_expr,
                    self.schema_expr)


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
                "schema nor a list of those".format( value))
        if isinstance(value, list):
            type_list = value
        else:
            type_list = [value]
        seen = set()
        for js_type in type_list:
            if isinstance(js_type, dict):
                # no nested validation here
                pass
            else:
                if js_type in seen:
                    raise SchemaError(
                        "type value {0!r} contains duplicate element"
                        " {1!r}".format( value, js_type))
                else:
                    seen.add(js_type)
                if js_type not in (
                    "string", "number", "integer", "boolean", "object",
                    "array", "null", "any"):
                    raise SchemaError(
                        "type value {0!r} is not a simple type "
                        "name".format(js_type))
        return type_list

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
                "schema nor a list of those".format( value))
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


class Validator(object):
    """
    JSON Schema validator.

    Can be used to validate any JSON document against a :class:`Schema`.
    """
    JSON_TYPE_MAP = {
        "string": basestring,
        "number": NUMERIC_TYPES,
        "integer": int,
        "object": dict,
        "array": list,
        "null": types.NoneType,
    }

    def __init__(self):
        self._schema_stack = []
        self._object_stack = []

    def _push_object(self, obj, path):
        self._object_stack.append((obj, path))

    def _pop_object(self):
        self._object_stack.pop()

    def _push_schema(self, schema, path):
        self._schema_stack.append((schema, path))

    def _pop_schema(self):
        self._schema_stack.pop()

    @property
    def _object(self):
        return self._object_stack[-1][0]

    @property
    def _schema(self):
        return self._schema_stack[-1][0]

    @classmethod
    def validate(cls, schema, obj):
        """
        Validate specified JSON object obj with specified Schema
        instance schema.

        :param schema: Schema to validate against
        :type schema: :class:`Schema`
        :param obj: JSON Document to validate
        :rtype: bool
        :returns: True on success
        :raises ValidationError: if the object does not match schema.
        :raises SchemaError: if the schema itself is wrong.
        """
        if not isinstance(schema, Schema):
            raise ValueError(
                "schema value {0!r} is not a Schema"
                " object".format(schema))
        self = cls()
        self.validate_toplevel(schema, obj)
        return True

    def _get_object_expression(self):
        return "".join(map(lambda x: x[1], self._object_stack))

    def _get_schema_expression(self):
        return "".join(map(lambda x: x[1], self._schema_stack))

    def validate_toplevel(self, schema, obj):
        self._object_stack = []
        self._schema_stack = []
        self._push_schema(schema, "schema")
        self._push_object(obj, "object")
        self._validate()
        self._pop_schema()
        self._pop_object()

    def _validate(self):
        obj = self._object
        self._validate_type()
        self._validate_requires()
        if isinstance(obj, dict):
            self._validate_properties()
            self._validate_additional_properties()
        elif isinstance(obj, list):
            self._validate_items()
        else:
            self._validate_enum()
            self._validate_format()
        self._report_unsupported()

    def _report_error(self, legacy_message, new_message=None,
                      schema_suffix=None):
        """
        Report an error during validation.

        There are two error messages. The legacy message is used for
        backwards compatibility and usually contains the object
        (possibly very large) that failed to validate. The new message
        is much better as it contains just a short message on what went
        wrong. User code can inspect object_expr and schema_expr to see
        which part of the object failed to validate against which part
        of the schema.

        The schema_suffix, if provided, is appended to the schema_expr.
        This is quite handy to specify the bit that the validator looked
        at (such as the type or optional flag, etc). object_suffix
        serves the same purpose but is used for object expressions
        instead.
        """
        object_expr = self._get_object_expression()
        schema_expr = self._get_schema_expression()
        if schema_suffix:
            schema_expr += schema_suffix
        raise ValidationError(legacy_message, new_message, object_expr,
                              schema_expr)

    def _push_property_schema(self, prop):
        """
        Construct a sub-schema from the value of the specified attribute
        of the current schema.
        """
        schema = Schema(self._schema.properties[prop])
        self._push_schema(schema, ".properties." + prop)

    def _push_additional_property_schema(self):
        schema = Schema(self._schema.additionalProperties)
        self._push_schema(schema, ".additionalProperties")

    def _push_array_schema(self):
        schema = Schema(self._schema.items)
        self._push_schema(schema, ".items")

    def _push_array_item_object(self, index):
        self._push_object(self._object[index], "[%d]" % index)

    def _push_property_object(self, prop):
        self._push_object(self._object[prop], "." + prop)

    def _report_unsupported(self):
        schema = self._schema
        if schema.minimum is not None:
            raise NotImplementedError("minimum is not supported")
        if schema.maximum is not None:
            raise NotImplementedError("maximum is not supported")
        if schema.minItems != 0:
            raise NotImplementedError("minItems is not supported")
        if schema.maxItems is not None:
            raise NotImplementedError("maxItems is not supported")
        if schema.uniqueItems != False:
            raise NotImplementedError("uniqueItems is not supported")
        if schema.pattern is not None:
            raise NotImplementedError("pattern is not supported")
        if schema.minLength != 0:
            raise NotImplementedError("minLength is not supported")
        if schema.maxLength is not None:
            raise NotImplementedError("maxLength is not supported")
        if schema.contentEncoding is not None:
            raise NotImplementedError("contentEncoding is not supported")
        if schema.divisibleBy != 1:
            raise NotImplementedError("divisibleBy is not supported")
        if schema.disallow is not None:
            raise NotImplementedError("disallow is not supported")

    def _validate_type(self):
        obj = self._object
        schema = self._schema
        for json_type in schema.type:
            if json_type == "any":
                return
            if json_type == "boolean":
                # Bool is special cased because in python there is no
                # way to test for isinstance(something, bool) that would
                # not catch isinstance(1, bool) :/
                if obj is not True and obj is not False:
                    self._report_error(
                        "{obj!r} does not match type {type!r}".format(
                            obj=obj, type=json_type),
                        "Object has incorrect type (expected boolean)",
                        schema_suffix=".type")
                break
            elif isinstance(json_type, dict):
                # Nested type check. This is pretty odd case. Here we
                # don't change our object stack (it's the same object).
                self._push_schema(Schema(json_type), ".type")
                self._validate()
                self._pop_schema()
                break
            else:
                # Simple type check
                if isinstance(obj, self.JSON_TYPE_MAP[json_type]):
                    # First one that matches, wins
                    break
        else:
            self._report_error(
                "{obj!r} does not match type {type!r}".format(
                    obj=obj, type=json_type),
                "Object has incorrect type (expected {type})".format(
                    type=json_type),
                schema_suffix=".type")

    def _validate_format(self):
        fmt = self._schema.format
        obj = self._object
        if fmt is None:
            return
        if fmt == 'date-time':
            try:
                DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
                datetime.datetime.strptime(obj, DATE_TIME_FORMAT)
            except ValueError:
                self._report_error(
                    "{obj!r} is not a string representing JSON date-time".format(
                        obj=obj),
                    "Object is not a string representing JSON date-time",
                    schema_suffix=".format")
        else:
            raise NotImplementedError("format {0!r} is not supported".format(format))

    def _validate_properties(self):
        obj = self._object
        schema = self._schema
        assert isinstance(obj, dict)
        for prop in schema.properties.iterkeys():
            self._push_property_schema(prop)
            if prop in obj:
                self._push_property_object(prop)
                self._validate()
                self._pop_object()
            else:
                if not self._schema.optional:
                    self._report_error(
                        "{obj!r} does not have property {prop!r}".format(
                            obj=obj, prop=prop),
                        "Object lacks property {prop!r}".format(
                            prop=prop),
                        schema_suffix=".optional")
            self._pop_schema()

    def _validate_additional_properties(self):
        obj = self._object
        assert isinstance(obj, dict)
        if self._schema.additionalProperties is False:
            # Additional properties are disallowed
            # Report exception for each unknown property
            for prop in obj.iterkeys():
                if prop not in self._schema.properties:
                    self._report_error(
                        "{obj!r} has unknown property {prop!r} and"
                        " additionalProperties is false".format(
                            obj=obj, prop=prop),
                        "Object has unknown property {prop!r} but"
                        " additional properties are disallowed".format(
                            prop=prop),
                        schema_suffix=".additionalProperties")
        else:
            # Check each property against this object
            self._push_additional_property_schema()
            for prop in obj.iterkeys():
                self._push_property_object(prop)
                self._validate()
                self._pop_object()
            self._pop_schema()

    def _validate_enum(self):
        obj = self._object
        schema = self._schema
        if schema.enum is not None:
            for allowed_value in schema.enum:
                if obj == allowed_value:
                    break
            else:
                self._report_error(
                    "{obj!r} does not match any value in enumeration"
                    " {enum!r}".format(obj=obj, enum=schema.enum),
                    "Object does not match any value in enumeration",
                    schema_suffix=".enum")

    def _validate_items(self):
        obj = self._object
        schema = self._schema
        assert isinstance(obj, list)
        items_schema_json = schema.items
        if items_schema_json == {}:
            # default value, don't do anything
            return
        if isinstance(items_schema_json, dict):
            self._push_array_schema()
            for index, item in enumerate(obj):
                self._push_array_item_object(index)
                self._validate()
                self._pop_object()
            self._pop_schema()
        elif isinstance(items_schema_json, list):
            if len(obj) < len(items_schema_json):
                # If our data array is shorter than the schema then
                # validation fails. Longer arrays are okay (during this
                # step) as they are validated based on
                # additionalProperties schema
                self._report_error(
                    "{obj!r} is shorter than array schema {schema!r}".
                    format(obj=obj, schema=items_schema_json),
                    "Object array is shorter than schema array",
                    schema_suffix=".items")
            if len(obj) != len(items_schema_json) and schema.additionalProperties is False:
                # If our array is not exactly the same size as the
                # schema and additional properties are disallowed then
                # validation fails
                self._report_error(
                    "{obj!r} is not of the same length as array schema"
                    " {schema!r} and additionalProperties is"
                    " false".format(obj=obj, schema=items_schema_json),
                    "Object array is not of the same length as schema array",
                    schema_suffix=".items")
            # Validate each array element using schema for the
            # corresponding array index, fill missing values (since
            # there may be more items in our array than in the schema)
            # with additionalProperties which by now is not False
            for index, (item, item_schema_json) in enumerate(
                itertools.izip_longest(
                    obj, items_schema_json,
                    fillvalue=schema.additionalProperties)):
                item_schema = Schema(item_schema_json)
                if index < len(items_schema_json):
                    self._push_schema(item_schema, "items[%d]" % index)
                else:
                    self._push_schema(item_schema, ".additionalProperties")
                self._push_array_item_object(index)
                self._validate()
                self._pop_schema()
                self._pop_object()

    def _validate_requires(self):
        obj = self._object
        schema = self._schema
        requires_json = schema.requires
        if requires_json == {}:
            # default value, don't do anything
            return
        # Find our enclosing object in the object stack
        if len(self._object_stack) < 2:
            self._report_error(
                "{obj!r} requires that enclosing object matches"
                " schema {schema!r} but there is no enclosing"
                " object".format(obj=obj, schema=requires_json),
                "Object has no enclosing object that matches schema",
                schema_suffix=".requires")
        # Note: Parent object can be None, (e.g. a null property)
        parent_obj = self._object_stack[-2][0]
        if isinstance(requires_json, basestring):
            # This is a simple property test
            if (not isinstance(parent_obj, dict)
                or requires_json not in parent_obj):
                self._report_error(
                    "{obj!r} requires presence of property {requires!r}"
                    " in the same object".format(
                        obj=obj, requires=requires_json),
                    "Enclosing object does not have property"
                    " {prop!r}".format(prop=requires_json),
                    schema_suffix=".requires")
        elif isinstance(requires_json, dict):
            # Requires designates a whole schema, the enclosing object
            # must match against that schema.
            # Here we resort to a small hack. Proper implementation
            # would require us to validate the parent object from its
            # own context (own list of parent objects). Since doing that
            # and restoring the state would be very complicated we just
            # instantiate a new validator with a subset of our current
            # history here.
            sub_validator = Validator()
            sub_validator._object_stack = self._object_stack[:-1]
            sub_validator._schema_stack = self._schema_stack[:]
            sub_validator._push_schema(
                Schema(requires_json), ".requires")
            sub_validator._validate()


def validate(schema_text, data_text):
    """
    Validate specified JSON text (data_text) with specified schema
    (schema text). Both are converted to JSON objects with
    :func:`simplesjon.loads`.
    """
    import simplejson as json
    schema = Schema(json.loads(schema_text))
    data = json.loads(data_text)
    return Validator.validate(schema, data)
