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
Unit tests for JSON schema
"""

import re
import simplejson

from testtools import TestCase
from testscenarios import TestWithScenarios

from linaro_json.schema import (
    Schema,
    SchemaError,
    ValidationError,
    validate,
)


class SchemaTests(TestWithScenarios, TestCase):

    scenarios = [
        ('type_default', {
            'schema': '{}',
            'expected': {
                'type': ['any']
            },
        }),
        ('type_string', {
            'schema': '{"type": "string"}',
            'expected': {
                'type': ['string']
            },
        }),
        ('type_number', {
            'schema': '{"type": "number"}',
            'expected': {
                'type': ['number']
            },
        }),
        ('type_integer', {
            'schema': '{"type": "integer"}',
            'expected': {
                'type': ['integer']
            },
        }),
        ('type_boolean', {
            'schema': '{"type": "boolean"}',
            'expected': {
                'type': ['boolean']
            },
        }),
        ('type_object', {
            'schema': '{"type": "object"}',
            'expected': {
                'type': ['object']
            },
        }),
        ('type_array', {
            'schema': '{"type": "array"}',
            'expected': {
                'type': ['array']
            },
        }),
        ('type_complex_subtype', {
            'schema': '{"type": {}}',
            'expected': {
                'type': [{}],
            },
        }),
        ('type_list', {
            'schema': '{"type": ["string", "number"]}',
            'expected': {
                'type': ["string", "number"],
            },
        }),
        ('type_wrong_type', {
            'schema': '{"type": 5}',
            'access': 'type',
            'raises': SchemaError(
                "type value 5 is not a simple type name,"
                " nested schema nor a list of those"),
        }),
        ('type_not_a_simple_type_name', {
            'schema': '{"type": "foobar"}',
            'access': 'type',
            'raises': SchemaError(
                "type value 'foobar' is not a simple type name"),
        }),
        ('type_list_duplicates', {
            'schema': '{"type": ["string", "string"]}',
            'access': 'type',
            'raises': SchemaError(
                "type value ['string', 'string'] contains duplicate"
                " element 'string'")
        }),
        ('properties_default', {
            'schema': '{}',
            'expected': {
                'properties': {},
            },
        }),
        ('properties_example', {
            'schema': '{"properties": {"prop": {"type": "number"}}}',
            'expected': {
                'properties': {"prop": {"type": "number"}},
            },
        }),
        ('properties_wrong_type', {
            'schema': '{"properties": 5}',
            'access': 'properties',
            'raises': SchemaError(
                'properties value 5 is not an object'),
        }),
        ('items_default', {
            'schema': '{}',
            'expected': {
                'items': {},
            },
        }),
        ('items_tuple', {
            'schema': '{"items": [{}, {}]}',
            'expected': {
                'items': [{}, {}],
            },
        }),
        ('items_each', {
            'schema': '{"items": {"type": "number"}}',
            'expected': {
                'items': {"type": "number"},
            },
        }),
        ('items_wrong_type', {
            'schema': '{"items": 5}',
            'access': 'items',
            'raises': SchemaError(
                'items value 5 is neither a list nor an object'),
        }),
        ('optional_default', {
            'schema': '{}',
            'expected': {
                'optional': False,
            },
        }),
        ('optional_true', {
            'schema': '{"optional": true}',
            'expected': {
                'optional': True,
            },
        }),
        ('optional_false', {
            'schema': '{"optional": false}',
            'expected': {
                'optional': False,
            },
        }),
        ('optional_wrong_type', {
            'schema': '{"optional": 5}',
            'access': 'optional',
            'raises': SchemaError(
                'optional value 5 is not a boolean'),
        }),
        ('additionalProperties_default', {
            'schema': '{}',
            'expected': {
                'additionalProperties': {}
            },
        }),
        ('additionalProperties_false', {
            'schema': '{"additionalProperties": false}',
            'expected': {
                "additionalProperties": False,
            },
        }),
        ('additionalProperties_object', {
            'schema': '{"additionalProperties": {"type": "number"}}',
            'expected': {
                "additionalProperties": {"type": "number"},
            },
        }),
        ('additionalProperties_wrong_type', {
            'schema': '{"additionalProperties": 5}',
            'access': 'additionalProperties',
            'raises': SchemaError(
                'additionalProperties value 5 is neither false nor an'
                ' object'),
        }),
        ('requires_default', {
            'schema': '{}',
            'expected': {
                'requires': {},
            },
        }),
        ('requires_property_name', {
            'schema': '{"requires": "other"}',
            'expected': {
                'requires': "other",
            },
        }),
        ('requires_schema', {
            'schema': '{"requires": {"properties": {"other": {"type": "number"}}}}',
            'expected': {
                'requires': {
                    'properties': {
                        'other': {
                            'type': 'number'
                        },
                    },
                },
            },
        }),
        ('requires_wrong_value', {
            'schema': '{"requires": 5}',
            'access': 'requires',
            'raises': SchemaError(
                'requires value 5 is neither a string nor an object'),
        }),
        ('minimum_default', {
            'schema': '{}',
            'expected': {
                'minimum': None
            },
        }),
        ('minimum_integer', {
            'schema': '{"minimum": 5}',
            'expected': {
                'minimum': 5
            },
        }),
        ('minimum_float', {
            'schema': '{"minimum": 3.5}',
            'expected': {
                'minimum': 3.5
            },
        }),
        ('minimum_wrong_type', {
            'schema': '{"minimum": "foobar"}',
            'access': 'minimum',
            'raises': SchemaError(
                'minimum value \'foobar\' is not a numeric type')
        }),
        ('maximum_default', {
            'schema': '{}',
            'expected': {
                'maximum': None
            },
        }),
        ('maximum_integer', {
            'schema': '{"maximum": 5}',
            'expected': {
                'maximum': 5
            },
        }),
        ('maximum_float', {
            'schema': '{"maximum": 3.5}',
            'expected': {
                'maximum': 3.5
            },
        }),
        ('maximum_wrong_type', {
            'schema': '{"maximum": "foobar"}',
            'access': 'maximum',
            'raises': SchemaError(
                'maximum value \'foobar\' is not a numeric type')
        }),
        ('minimumCanEqual_default', {
            'schema': '{"minimum": 5}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': True
            },
        }),
        ('minimumCanEqual_false', {
            'schema': '{"minimum": 5, "minimumCanEqual": false}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': False,
            },
        }),
        ('minimumCanEqual_true', {
            'schema': '{"minimum": 5, "minimumCanEqual": true}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': True
            },
        }),
        ('minimumCanEqual_without_minimum', {
            'schema': '{}',
            'access': 'minimumCanEqual',
            'raises': SchemaError(
                "minimumCanEqual requires presence of minimum"),
        }),
        ('minimumCanEqual_wrong_type', {
            'schema': '{"minimum": 5, "minimumCanEqual": 5}',
            'access': 'minimumCanEqual',
            'raises': SchemaError(
                "minimumCanEqual value 5 is not a boolean"),
        }),
        ('maximumCanEqual_default', {
            'schema': '{"maximum": 5}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': True
            },
        }),
        ('maximumCanEqual_false', {
            'schema': '{"maximum": 5, "maximumCanEqual": false}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': False,
            },
        }),
        ('maximumCanEqual_true', {
            'schema': '{"maximum": 5, "maximumCanEqual": true}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': True
            },
        }),
        ('maximumCanEqual_without_maximum', {
            'schema': '{}',
            'access': 'maximumCanEqual',
            'raises': SchemaError(
                "maximumCanEqual requires presence of maximum"),
        }),
        ('maximumCanEqual_wrong_type', {
            'schema': '{"maximum": 5, "maximumCanEqual": 5}',
            'access': 'maximumCanEqual',
            'raises': SchemaError(
                "maximumCanEqual value 5 is not a boolean"),
        }),
        ("minItems_default", {
            'schema': '{}',
            'expected': {
                'minItems': 0,
            },
        }),
        ("minItems_integer", {
            'schema': '{"minItems": 13}',
            'expected': {
                'minItems': 13,
            },
        }),
        ("minItems_zero", {
            'schema': '{"minItems": 0}',
            'expected': {
                'minItems': 0,
            },
        }),
        ("minItems_minus_one", {
            'schema': '{"minItems": -1}',
            'access': 'minItems',
            'raises': SchemaError(
                "minItems value -1 cannot be negative"),
        }),
        ("minItems_wrong_type", {
            'schema': '{"minItems": "foobar"}',
            'access': 'minItems',
            'raises': SchemaError(
                "minItems value 'foobar' is not an integer"),
        }),
        ("maxItems_default", {
            'schema': '{}',
            'expected': {
                'maxItems': None,
            },
        }),
        ("maxItems_integer", {
            'schema': '{"maxItems": 13}',
            'expected': {
                'maxItems': 13,
            },
        }),
        ("maxItems_zero", {
            'schema': '{"maxItems": 0}',
            'expected': {
                'maxItems': 0,
            },
        }),
        ("maxItems_minus_one", {
            'schema': '{"maxItems": -1}',
            'expected': {
                'maxItems': -1
            },
        }),
        ("maxItems_wrong_type", {
            'schema': '{"maxItems": "foobar"}',
            'access': 'maxItems',
            'raises': SchemaError(
                "maxItems value 'foobar' is not an integer"),
        }),
        ("uniqueItems_default", {
            'schema': '{}',
            'expected': {
                'uniqueItems': False
            }
        }),
        ("uniqueItems_true", {
            'schema': '{"uniqueItems": true}',
            'expected': {
                'uniqueItems': True
            }
        }),
        ("uniqueItems_false", {
            'schema': '{"uniqueItems": false}',
            'expected': {
                'uniqueItems': False
            }
        }),
        ("uniqueItems_wrong_type", {
            'schema': '{"uniqueItems": 5}',
            'access': 'uniqueItems',
            'raises': SchemaError(
                "uniqueItems value 5 is not a boolean")
        }),
        ("pattern_default", {
            'schema': '{}',
            'expected': {
                'pattern': None,
            },
        }),
        #("pattern_simple", {
        #    'schema': '{"pattern": "foo|bar"}',
        #    'expected': {
        #        'pattern': re.compile('foo|bar'),
        #    },
        #}),
        ("pattern_broken", {
            'schema': '{"pattern": "[unterminated"}',
            'access': 'pattern',
            'raises': SchemaError(
                "pattern value '[unterminated' is not a valid regular"
                " expression: unexpected end of regular expression"),
        }),
        ("minLength_default", {
            'schema': '{}',
            'expected': {
                'minLength': 0,
            },
        }),
        ("minLength_integer", {
            'schema': '{"minLength": 13}',
            'expected': {
                'minLength': 13,
            },
        }),
        ("minLength_zero", {
            'schema': '{"minLength": 0}',
            'expected': {
                'minLength': 0,
            },
        }),
        ("minLength_minus_one", {
            'schema': '{"minLength": -1}',
            'access': 'minLength',
            'raises': SchemaError(
                "minLength value -1 cannot be negative"),
        }),
        ("minLength_wrong_type", {
            'schema': '{"minLength": "foobar"}',
            'access': 'minLength',
            'raises': SchemaError(
                "minLength value 'foobar' is not an integer"),
        }),
        ("maxLength_default", {
            'schema': '{}',
            'expected': {
                'maxLength': None,
            },
        }),
        ("maxLength_integer", {
            'schema': '{"maxLength": 13}',
            'expected': {
                'maxLength': 13,
            },
        }),
        ("maxLength_zero", {
            'schema': '{"maxLength": 0}',
            'expected': {
                'maxLength': 0,
            },
        }),
        ("maxLength_minus_one", {
            'schema': '{"maxLength": -1}',
            'expected': {
                'maxLength': -1
            },
        }),
        ("maxLength_wrong_type", {
            'schema': '{"maxLength": "foobar"}',
            'access': 'maxLength',
            'raises': SchemaError(
                "maxLength value 'foobar' is not an integer"),
        }),
        ("enum_default", {
            'schema': '{}',
            'expected': {
                'enum': None,
            }
        }),
        ("enum_simple", {
            'schema': '{"enum": ["foo", "bar"]}',
            'expected': {
                'enum': ["foo", "bar"],
            }
        }),
        ("enum_mixed", {
            'schema': '{"enum": [5, false, "foobar"]}',
            'expected': {
                'enum':[5, False, "foobar"]
            }
        }),
        ("enum_wrong_type", {
            'schema': '{"enum": "foobar"}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value 'foobar' is not a list"),
        }),
        ("enum_too_short", {
            'schema': '{"enum": []}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value [] does not contain any elements"),
        }),
        ("enum_duplicates", {
            'schema': '{"enum": ["foo", "foo"]}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value ['foo', 'foo'] contains duplicate element"
                " 'foo'"),
        }),
        ("title_default", {
            'schema': '{}',
            'expected': {
                'title': None,
            },
        }),
        ("title_simple", {
            'schema': '{"title": "foobar"}',
            'expected': {
                'title': "foobar",
            },
        }),
        ("title_wrong_type", {
            'schema': '{"title": 5}',
            'access': 'title',
            'raises': SchemaError('title value 5 is not a string')
        }),
        ("description_default", {
            'schema': '{}',
            'expected': {
                'description': None,
            },
        }),
        ("description_simple", {
            'schema': '{"description": "foobar"}',
            'expected': {
                'description': "foobar",
            },
        }),
        ("description_wrong_type", {
            'schema': '{"description": 5}',
            'access': 'description',
            'raises': SchemaError('description value 5 is not a string')
        }),
        ("format_default", {
            'schema': '{}',
            'expected': {
                'format': None
            },
        }),
        ("format_date_time", {
            'schema': '{"format": "date-time"}',
            'expected': {
                'format': "date-time"
            },
        }),
        ("format_wrong_type", {
            'schema': '{"format": 5}',
            'access': 'format',
            'raises': SchemaError('format value 5 is not a string')
        }),
        ("format_not_implemented", {
            'schema': '{"format": "color"}',
            'access': 'format',
            'raises': NotImplementedError(
                "format value 'color' is not supported")
        }),
        ("contentEncoding_default", {
            'schema': '{}',
            'expected': {
                'contentEncoding': None,
            }
        }),
        ("contentEncoding_base64", {
            'schema': '{"contentEncoding": "base64"}',
            'expected': {
                'contentEncoding': "base64",
            },
        }),
        ("contentEncoding_base64_mixed_case", {
            'schema': '{"contentEncoding": "BAsE64"}',
            'expected': {
                'contentEncoding': 'BAsE64',
            },
        }),
        ("contentEncoding_unsupported_value", {
            'schema': '{"contentEncoding": "x-token"}',
            'access': 'contentEncoding',
            'raises': NotImplementedError(
                "contentEncoding value 'x-token' is not supported")
        }),
        ("contentEncoding_unknown_value", {
            'schema': '{"contentEncoding": "bogus"}',
            'access': 'contentEncoding',
            'raises': SchemaError(
                "contentEncoding value 'bogus' is not valid")
        }),
        ("divisibleBy_default", {
            'schema': '{}',
            'expected': {
                'divisibleBy': 1
            }
        }),
        ("divisibleBy_int", {
            'schema': '{"divisibleBy": 5}',
            'expected': {
                'divisibleBy': 5
            }
        }),
        ("divisibleBy_float", {
            'schema': '{"divisibleBy": 3.5}',
            'expected': {
                'divisibleBy': 3.5
            }
        }),
        ("divisibleBy_wrong_type", {
            'schema': '{"divisibleBy": "foobar"}',
            'access': 'divisibleBy',
            'raises': SchemaError(
                "divisibleBy value 'foobar' is not a numeric type")
        }),
        ("divisibleBy_minus_one", {
            'schema': '{"divisibleBy": -1}',
            'access': 'divisibleBy',
            'raises': SchemaError(
                "divisibleBy value -1 cannot be negative")
        }),
        ('disallow_default', {
            'schema': '{}',
            'expected': {
                'disallow': None
            },
        }),
        ('disallow_string', {
            'schema': '{"disallow": "string"}',
            'expected': {
                'disallow': ['string']
            },
        }),
        ('disallow_number', {
            'schema': '{"disallow": "number"}',
            'expected': {
                'disallow': ['number']
            },
        }),
        ('disallow_integer', {
            'schema': '{"disallow": "integer"}',
            'expected': {
                'disallow': ['integer']
            },
        }),
        ('disallow_boolean', {
            'schema': '{"disallow": "boolean"}',
            'expected': {
                'disallow': ['boolean']
            },
        }),
        ('disallow_object', {
            'schema': '{"disallow": "object"}',
            'expected': {
                'disallow': ['object']
            },
        }),
        ('disallow_array', {
            'schema': '{"disallow": "array"}',
            'expected': {
                'disallow': ['array']
            },
        }),
        ('disallow_complex_subtype', {
            'schema': '{"disallow": {}}',
            'expected': {
                'disallow': [{}],
            },
        }),
        ('disallow_list', {
            'schema': '{"disallow": ["string", "number"]}',
            'expected': {
                'disallow': ["string", "number"],
            },
        }),
        ('disallow_wrong_type', {
            'schema': '{"disallow": 5}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value 5 is not a simple type name,"
                " nested schema nor a list of those"),
        }),
        ('disallow_not_a_simple_disallow_name', {
            'schema': '{"disallow": "foobar"}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value 'foobar' is not a simple type name")
        }),
        ('disallow_list_duplicates', {
            'schema': '{"disallow": ["string", "string"]}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value ['string', 'string'] contains"
                " duplicate element 'string'")
        }),
        ('extends_not_supported', {
            'schema': '{}',
            'access': 'extends',
            'raises': NotImplementedError(
                "extends property is not supported"),
        }),
        ('default_with_value', {
            'schema': '{"default": 5}',
            'expected': {
                'default': 5
            }
        }),
        ('default_without_value', {
            'schema': '{}',
            'access': 'default',
            'raises': SchemaError("There is no schema default for this item"),
        }),
    ]

    def test_schema_attribute(self):
        schema = Schema(simplejson.loads(self.schema))
        if hasattr(self, 'expected'):
            for attr, expected_value in self.expected.iteritems():
                self.assertEqual(
                    expected_value, getattr(schema, attr))
        elif hasattr(self, 'access') and hasattr(self, 'raises'):
            self.assertRaises(
                type(self.raises),
                getattr, schema, self.access)
            try:
                getattr(schema, self.access)
            except type(self.raises) as ex:
                self.assertEqual(str(ex), str(self.raises))
            except Exception as ex:
                self.fail("Raised exception {0!r} instead of {1!r}".format(
                    ex, self.raises))
        else:
            self.fail("Broken test definition, must define 'expected' "
                      "or 'access' and 'raises' scenario attributes")


class ValidatorFailureTests(TestWithScenarios, TestCase):

    scenarios = [
        ("type_string_got_null", {
            'schema': '{"type": "string"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_string_got_integer", {
            'schema': '{"type": "string"}',
            'data': '5',
            'raises': ValidationError(
                "5 does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_null", {
            'schema': '{"type": "number"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_string", {
            'schema': '{"type": "number"}',
            'data': '"foobar"',
            'raises': ValidationError(
                "'foobar' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_string_that_looks_like_number", {
            'schema': '{"type": "number"}',
            'data': '"3"',
            'raises': ValidationError(
                "'3' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_integer_got_float", {
            'schema': '{"type": "integer"}',
            'data': '1.1',
            'raises': ValidationError(
                "1.1000000000000001 does not match type 'integer'",
                "Object has incorrect type (expected integer)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_integer_got_null", {
            'schema': '{"type": "integer"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'integer'",
                "Object has incorrect type (expected integer)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_null", {
            'schema': '{"type": "boolean"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_string", {
            'schema': '{"type": "boolean"}',
            'data': '""',
            'raises': ValidationError(
                "'' does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_list", {
            'schema': '{"type": "boolean"}',
            'data': '[]',
            'raises': ValidationError(
                "[] does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_object", {
            'schema': '{"type": "boolean"}',
            'data': '{}',
            'raises': ValidationError(
                "{} does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_object_got_integer", {
            'schema': '{"type": "object"}',
            'data': '1',
            'raises': ValidationError(
                "1 does not match type 'object'",
                "Object has incorrect type (expected object)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_object_got_null", {
            'schema': '{"type": "object"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'object'",
                "Object has incorrect type (expected object)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_array_got_null", {
            'schema': '{"type": "array"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'array'",
                "Object has incorrect type (expected array)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_array_got_integer", {
            'schema': '{"type": "array"}',
            'data': '1',
            'raises': ValidationError(
                "1 does not match type 'array'",
                "Object has incorrect type (expected array)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_string", {
            'schema': '{"type": "null"}',
            'data': '""',
            'raises': ValidationError(
                "'' does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_zero", {
            'schema': '{"type": "null"}',
            'data': '0',
            'raises': ValidationError(
                "0 does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_list", {
            'schema': '{"type": "null"}',
            'data': '[]',
            'raises': ValidationError(
                "[] does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_object", {
            'schema': '{"type": "null"}',
            'data': '{}',
            'raises': ValidationError(
                "{} does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("property_check_is_not_primitive", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number"
                    }
                }
            }""",
            'data': '{"foo": "foobar"}',
            'raises': ValidationError(
                "'foobar' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.foo.type',
        }),
        ("property_check_validates_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": true
                    }
                }
            }""",
            'data': '{"foo": null}',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.foo.type',
        }),
        ("property_check_reports_missing_non_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": false
                    }
                }
            }""",
            'data': '{}',
            'raises': ValidationError(
                "{} does not have property 'foo'",
                "Object lacks property 'foo'"),
            'object_expr': 'object',
            'schema_expr': 'schema.properties.foo.optional',
        }),
        ("property_check_reports_unknown_properties_when_additionalProperties_is_false", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": false
            }""",
            'data': '{"foo": 5}',
            'raises': ValidationError(
                "{'foo': 5} has unknown property 'foo' and"
                " additionalProperties is false",
                "Object has unknown property 'foo' but additional "
                "properties are disallowed"),
            'object_expr': 'object',
            'schema_expr': 'schema.additionalProperties',
        }),
        ("property_check_validates_additional_properties_using_specified_type_when_additionalProperties_is_an_object_violation", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                }
            }""",
            'data': '{"foo": "aaa", "bar": 5}',
            'raises': ValidationError(
                "5 does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object.bar',
            'schema_expr': 'schema.additionalProperties.type',
        }),
        ("enum_check_reports_unlisted_values", {
            'schema': '{"enum": [1, 2, 3]}',
            'data': '5',
            'raises': ValidationError(
                '5 does not match any value in enumeration [1, 2, 3]',
                "Object does not match any value in enumeration"),
            'object_expr': 'object',
            'schema_expr': 'schema.enum',
        }),
        ("items_with_single_schema_finds_problems", {
            'schema': '{"items": {"type": "string"}}',
            'data': '["foo", null, "froz"]',
            'raises': ValidationError(
                "None does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object[1]',
            'schema_expr': 'schema.items.type',
        }),
        ("items_with_array_schema_checks_for_too_short_data", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ]
            }""",
            'data': '["foo"]',
            'raises': ValidationError(
                "['foo'] is shorter than array schema [{'type':"
                " 'string'}, {'type': 'boolean'}]",
                "Object array is shorter than schema array"),
            'object_expr': 'object',
            'schema_expr': 'schema.items',
        }),
        ("items_with_array_schema_and_additionalProperties_of_false_checks_for_too_much_data", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": false
            }""",
            'data': '["foo", false, 5]',
            'raises': ValidationError(
                "['foo', False, 5] is not of the same length as array"
                " schema [{'type': 'string'}, {'type': 'boolean'}] and"
                " additionalProperties is false",
                "Object array is not of the same length as schema array"),
            'object_expr': 'object',
            'schema_expr': 'schema.items',
        }),
        ("items_with_array_schema_and_additionalProperties_can_find_problems", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": {
                    "type": "number"
                }
            }""",
            'data': '["foo", false, 5, 7.9, null]',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object[4]',
            'schema_expr': 'schema.additionalProperties.type',
        }),
        ("requires_with_simple_property_name_can_report_problems", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null}',
            'raises': ValidationError(
                "None requires presence of property 'foo' in the same"
                " object",
                "Enclosing object does not have property 'foo'"),
            'object_expr': 'object.bar',
            'schema_expr': 'schema.properties.bar.requires',
        }),
        ("requires_with_simple_property_name_can_report_problems_while_nested", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "nested": {
                        "properties": {
                            "foo": {
                                "optional": true
                            },
                            "bar": {
                                "requires": "foo",
                                "optional": true
                            }
                        }
                    }
                }
            }
            """,
            'data': '{"nested": {"bar": null}}',
            'raises': ValidationError(
                "None requires presence of property 'foo' in the same"
                " object",
                "Enclosing object does not have property 'foo'"),
            'object_expr': 'object.nested.bar',
            'schema_expr': 'schema.properties.nested.properties.bar.requires',
        }),
        ("requires_with_schema_can_report_problems", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null}',
            'raises': ValidationError(
                "{'bar': None} does not have property 'foo'",
                "Object lacks property 'foo'"),
            'object_expr': 'object',
            'schema_expr': 'schema.properties.bar.requires.properties.foo.optional',
        }),
        ("requires_with_schema_can_report_subtle_problems", {
            # In this test presence of "bar" requires that "foo" is
            # present and has a type "number"
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null, "foo": "not a number"}',
            'raises': ValidationError(
                "'not a number' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.bar.requires.properties.foo.type'
        }),
        ("format_date_time_finds_problems", {
            'schema': '{"format": "date-time"}',
            'data': '"broken"',
            'raises': ValidationError(
                "'broken' is not a string representing JSON date-time",
                "Object is not a string representing JSON date-time"),
            'object_expr': 'object',
            'schema_expr': 'schema.format'
        }),
    ]

    def test_validation_error_has_proper_message(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.message, self.raises.message)

    def test_validation_error_has_proper_new_message(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.new_message, self.raises.new_message)

    def test_validation_error_has_proper_object_expr(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.object_expr, self.object_expr)

    def test_validation_error_has_proper_schema_expr(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.schema_expr, self.schema_expr)


class ValidatorSuccessTests(TestWithScenarios, TestCase):

    scenarios = [
        ("type_string_got_string", {
            'schema': '{"type": "string"}',
            'data': '"foobar"'
        }),
        ("type_number_got_integer", {
            'schema': '{"type": "number"}',
            'data': '1',
        }),
        ("type_number_number_float", {
            'schema': '{"type": "number"}',
            'data': '1.1',
        }),
        ("type_integer_got_integer_one", {
            'schema': '{"type": "integer"}',
            'data': '1'
        }),
        ("type_integer_got_integer", {
            'schema': '{"type": "integer"}',
            'data': '5'
        }),
        ("type_boolean_got_true", {
            'schema': '{"type": "boolean"}',
            'data': 'true',
        }),
        ("type_boolean_got_false", {
            'schema': '{"type": "boolean"}',
            'data': 'true',
        }),
        ("type_object_got_object", {
            'schema': '{"type": "object"}',
            'data': '{}'
        }),
        ("type_array_got_array", {
            'schema': '{"type": "array"}',
            'data': '[]'
        }),
        ("type_null_got_null", {
            'schema': '{"type": "null"}',
            'data': 'null',
        }),
        ("type_any_got_null", {
            'schema': '{"type": "any"}',
            'data': 'null',
        }),
        ("type_any_got_integer", {
            'schema': '{"type": "any"}',
            'data': '5',
        }),
        ("type_any_got_boolean", {
            'schema': '{"type": "any"}',
            'data': 'false',
        }),
        ("type_any_got_string", {
            'schema': '{"type": "any"}',
            'data': '"foobar"',
        }),
        ("type_any_got_array", {
            'schema': '{"type": "any"}',
            'data': '[]',
        }),
        ("type_any_got_object", {
            'schema': '{"type": "any"}',
            'data': '{}',
        }),
        ("type_nested_schema_check", {
            'schema': '{"type": {"type": "number"}}',
            'data': '5',
        }),
        ("property_ignored_on_non_objects", {
            'schema': '{"properties": {"foo": {"type": "number"}}}',
            'data': '"foobar"',
        }),
        ("property_checks_known_props", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number"
                    },
                    "bar": {
                        "type": "boolean"
                    }
                }
            }""",
            'data': """
            {
                "foo": 5,
                "bar": false
            }"""
        }),
        ("property_check_ignores_missing_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": true
                    }
                }
            }""",
            'data': '{}',
        }),
        ("property_check_ignores_normal_properties_when_additionalProperties_is_false", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {}
                },
                "additionalProperties": false
            }""",
            'data': '{"foo": 5}',
        }),
        ("property_check_validates_additional_properties_using_specified_type_when_additionalProperties_is_an_object", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                }
            }""",
            'data': '{"foo": "aaa", "bar": "bbb"}',
        }),
        ("enum_check_does_nothing_by_default", {
            'schema': '{}',
            'data': '5',
        }),
        ("enum_check_verifies_possible_values", {
            'schema': '{"enum": [1, 2, 3]}',
            'data': '2',
        }),
        ("items_check_does_nothing_for_non_arrays", {
            'schema': '{"items": {"type": "string"}}',
            'data': '5',
        }),
        ("items_with_single_schema_applies_to_each_item", {
            'schema': '{"items": {"type": "string"}}',
            'data': '["foo", "bar", "froz"]',
        }),
        ("items_with_array_schema_applies_to_corresponding_items", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ]
            }""",
            'data': '["foo", true]',
        }),
        ("items_with_array_schema_and_additionalProperties", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": {
                    "type": "number"
                }
            }""",
            'data': '["foo", false, 5, 7.9]',
        }),
        ("requires_with_simple_property_name_does_nothing_when_parent_property_is_not_used", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{}',
        }),
        ("requires_with_simple_property_name_works_when_condition_satisfied", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"foo": null, "bar": null}',
        }),
        ("requires_with_schema_name_does_nothing_when_parent_property_is_not_used", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{}',
        }),
        ("format_date_time_works", {
            'schema': '{"format": "date-time"}',
            'data': '"2010-11-12T14:38:55Z"',
        }),
    ]

    def test_validator_does_not_raise_an_exception(self):
        self.assertEqual(
            True, validate(self.schema, self.data))
