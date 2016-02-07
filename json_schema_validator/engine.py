# encoding: utf-8
# Copyright (C) 2016 Zygmunt Krynicki
#
# Author: Zygmunt Krynicki <me@zygoon.pl>
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

"""New validation engine."""

from __future__ import absolute_import, print_function

from json_schema_validator.errors import FastValidationFailure
from json_schema_validator.errors import SchemaError
from json_schema_validator.errors import ValidationError
from json_schema_validator.misc import NUMERIC_TYPES
from json_schema_validator.misc import INTEGER_TYPES
from json_schema_validator.misc import STRING_TYPES


class pointer(object):

    """Primitive implementation of JSON pointer."""

    def __init__(self, parts):
        self.parts = parts

    def __repr__(self):
        return "pointer({!r})".format(self.parts)

    def __str__(self):
        return '/'.join(str(part) for part in self.parts)

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, pointer):
            return self.parts == other.parts
        return False


class Fragment(object):
    """
    Fragment for checking part of a schema.

    Fragments are the building block of the engine. Each fragment is
    responsible for one aspect of the schema. This design makes it easy to test
    particular fragments and still reason about the correctness of a
    composition of multiple fragments.

    Each fragment knows how to "compile" a schema into a fast path analysis and
    a recovery path analysis. Fast path assumes that objects are valid and does
    bare minimum required to verify that. Recovery path assumes that objects
    are not valid and works on creating a useful and descriptive error.
    """

    def __init__(self, schema):
        """
        Initialize the fragment checker.

        :param schema:
            Schema object to analyze.
        :raises SchemaError:
            If the schema is incorrect.
        """
        self.schema = schema

    def fast_cmds(self):
        """
        Generate fast path commands.

        :returns:
            Generator of fast path commands.

        Each fast path command is a callable ``fn(obj)`` that when called with
        an object (validate object instance) returns True if the object is
        valid.
        """

    def recovery_cmds(self):
        pass

    def assertValid(self, obj):
        """
        Assert that a object is valid.

        Validation is performed to the extent described by the fragment.

        :param obj:
            Object to validate.
        :raises AssertionError:
            If validation fails
        """
        for cmd in self.fast_cmds():
            if cmd(obj) is False:
                raise AssertionError(
                    "{!r} is not valid according to {!r}".format(
                        obj, self.schema))

    def assertNotValid(self, obj):
        """
        Assert that a object is not valid.

        Validation is performed to the extent described by the fragment.

        :param obj:
            Object to validate.
        :raises AssertionError:
            If validation fails
        """
        for cmd in self.fast_cmds():
            if cmd(obj) is True:
                raise AssertionError(
                    "{!r} is valid according to {!r}".format(
                        obj, self.schema))


class TypeFragment(Fragment):
    """
    Fragment implementing the "type" schema attribute.

    This attribute defines what the primitive type or the schema of the
    instance MUST be in order to validate.  This attribute can take one
    of two forms:

    Simple Types.

    A string indicating a primitive or simple type.  The following are
    acceptable string values:

      string:
          Value MUST be a string.

      number:
          Value MUST be a number, floating point numbers are allowed.

      integer:
          Value MUST be an integer, no floating point numbers are allowed.
          This is a subset of the number type.

      boolean:
          Value MUST be a boolean.

      object:
          Value MUST be an object.

      array:
          Value MUST be an array.

      null:
          Value MUST be null.  Note this is mainly for purpose of being able
          use union types to define nullability.  If this type is not included
          in a union, null values are not allowed (the primitives listed above
          do not allow nulls on their own).

      any:
          Value MAY be of any type including null.

      If the property is not defined or is not in this list, then any type of
      value is acceptable.  Other type values MAY be used for custom purposes,
      but minimal validators of the specification implementation can allow any
      instance value on unknown type values.

   Union Types.

   An array of two or more simple type definitions.  Each item in the array
   MUST be a simple type definition or a schema.  The instance value is valid
   if it is of the same type as one of the simple type definitions, or valid by
   one of the schemas, in the array.

   For example, a schema that defines if an instance can be a string or a
   number would be::

        {"type":["string","number"]}
    """
    _type_names = {"string", "number", "integer", "boolean", "object",
                   "array", "null", "any"}

    _js_to_py = {
        'string': set(STRING_TYPES),
        'number': set(NUMERIC_TYPES),
        'integer': set(INTEGER_TYPES),
        'boolean': {bool, },
        'object': {dict, },
        'array': {list, },
        'null': {type(None), },
        'any': {object, },
    }

    def __init__(self, schema):
        super(TypeFragment, self).__init__(schema)
        js_type = schema.get('type')
        if js_type is None:
            js_types = set()
        elif isinstance(js_type, str):
            js_types = {js_type}
        elif isinstance(js_type, list):
            js_types = set(js_type)
            if len(js_types) < 2:
                raise SchemaError(
                    "union types must contain at least two simple types",
                    schema)
        else:
            raise SchemaError(
                "invalid kind of type constraint: {}".format(
                    type(js_type).__name__), schema)
        python_types = set()
        for js_type in js_types:
            try:
                python_types.update(self._js_to_py[js_type])
            except KeyError:
                # NOTE: this might not be an actual error. Specs recommend
                # to ignore unknown type names.
                raise SchemaError(
                    "unsupported type name: {!r}".format(js_type), schema)
        if 'any' in js_types:
            self.python_types = (object,)
        else:
            self.python_types = tuple(python_types)

    def fast_cmds(self):
        python_types = self.python_types
        if object in python_types:
            # If 'any' was used then there are no tests to perform
            pass
        elif bool in python_types:
            # If 'boolean' was used then naive python test is sufficient
            yield lambda obj: isinstance(obj, python_types)
        else:
            # If 'boolean' was not used then we must explicitly check for bool
            # instances.  This is caused by the fact that in Python
            # ``isinstance(True, int) is True`` but this is not the expected
            # behavior for ``true`` being valid under the schema ``{"type",
            # "int"}``
            assert isinstance(True, int)
            yield lambda obj: (
                not isinstance(obj, bool) and
                isinstance(obj, python_types))

    def recovery_cmds(self):
        if self.python_types:
            yield self._recovery

    def _recovery(self, obj, obj_path, schema_path):
        if not isinstance(obj, self.python_types):
            raise ValidationError(
                "N/A",
                "Object has incorrect type (expected {})".format(
                    self.schema["type"]),
                pointer(obj_path), pointer(schema_path + ["", "type"]))


class Validator(object):
    """Validator transforms schema for efficient validation."""

    _fragment_classes = {
        "http://json-schema.org/schema#": (
            # JSON Schema written against the current version of the
            # specification.
            TypeFragment,
        ),
        "http://json-schema.org/hyper-schema#": (
            # JSON Schema written against the current version of the
            # specification.

            # TODO: implement this
        ),
        "http://json-schema.org/draft-04/schema#": (
            # JSON Schema written against this version.

            # TODO: implement this
        ),
        "http://json-schema.org/draft-04/hyper-schema#": (
            # JSON Schema hyperschema written against this version.

            # TODO: implement this
        ),
        "http://json-schema.org/draft-03/schema#": (
            # JSON Schema written against JSON Schema,

            # TODO: implement this
        ),
        "http://json-schema.org/draft-03/hyper-schema#": (
            # JSON Schema hyperschema written against JSON Schema, draft v3

            # TODO: implement this
        ),
    }

    def __init__(self, schema):
        """
        Compile the specified schema.

        :param schema:
            Schema object to compile
        :raises SchemaError:
            If the schema is incorrect.
        """
        if not isinstance(schema, dict):
            raise SchemaError(
                "unexpected schema type {} (wanted dict)",
                type(schema).__name__, schema)
        _schema = schema.get("$schema", "http://json-schema.org/schema#")
        try:
            fragment_classes = self._fragment_classes[_schema]
        except KeyError:
            raise SchemaError("unsupported value of $schema: {!r}", _schema)
        self.schema = schema
        self.fast_cmds = []
        self.recovery_cmds = []
        for frag_cls in fragment_classes:
            frag = frag_cls(schema)
            self.fast_cmds.extend(frag.fast_cmds())
            self.recovery_cmds.extend(frag.recovery_cmds())

    def __call__(self, obj):
        """
        Validate the given object against a compiled schema.

        :param obj:
            Object to validate.
        :returns True:
            When the object is valid
        :raises ValidationError:
            When the object is not valid
        """
        try:
            for cmd in self.fast_cmds:
                if cmd(obj) is not True:
                    raise FastValidationFailure(obj, self.schema)
        except FastValidationFailure:
            obj_path = []
            sch_path = []
            for cmd in self.recovery_cmds:
                cmd(obj, obj_path, sch_path)
            assert False, "recovery path did not raise an exception"
        else:
            return True
