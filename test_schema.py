import unittest
import testscenarios
import simplejson

from schema import (
    validate, Schema, Validator, SchemaError, ValidationError)

class SchemaTests(unittest.TestCase):

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
                'type value 5 is not a simple type name, '
                'nested schema nor a list of those'),
        }),
        ('type_not_a_simple_type_name', {
            'schema': '{"type": "foobar"}',
            'access': 'type',
            'raises': SchemaError(
                'type value \'foobar\' is not a simple type name'),
        }),
        ('type_list_duplicates', {
            'schema': '{"type": ["string", "string"]}',
            'access': 'type',
            'raises': SchemaError(
                'type value [\'string\', \'string\'] contains duplicate'
                ' element \'string\'')
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
    ]

    def test_schema_attribute(self):
        schema = Schema(simplejson.loads(self.schema))
        if hasattr(self, 'expected'):
            for attr, expected_value in self.expected.iteritems():
                self.assertEqual(expected_value, getattr(schema, attr))
        elif hasattr(self, 'access') and hasattr(self, 'raises'):
            self.assertRaises(
                type(self.raises),
                getattr, schema, self.access)
            try:
                getattr(schema, self.access)
            except type(self.raises) as ex:
                self.assertEqual(str(self.raises), str(ex))
            except Exception as ex:
                self.fail("Raised exception {0!r} instead of {1!r}".format(
                    ex, self.raises))
        else:
            self.fail("Broken test definition, must define 'expected' "
                      "or 'access' and 'raises' scenario attributes")


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    tests = loader.loadTestsFromName(__name__)
    test_suite.addTests(testscenarios.generate_scenarios(tests))
    return test_suite

if __name__ == "__main__":
    unittest.main()
