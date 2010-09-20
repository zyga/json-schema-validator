#!/usr/bin/python
"""
JSON schema validator for python
Note: only a subset of schema features are currently supported.

See: json-schema.org for details
"""
import decimal
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
    A bug in the validated object prevents the program from working
    """


class Schema(object):
    """
    JSON schema object
    """

    def __init__(self, json_obj):
        """
        Initialize schema with JSON object

        Note: JSON objects are just plain python dictionaries
        """
        if not isinstance(json_obj, dict):
            raise SchemaError("Schema definition must be a JSON object")
        self._schema = json_obj

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
        Note: JSON schema specifications says that this value SHOULD
        follow the EMCA 262/Perl 5 format. We cannot support this so we
        support python regular expressions instead. This is still valid
        but should be noted for clarity.

        The return value is either None or a compiled regular expression
        object
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
        value = self._schema.get("maxLength", 0)
        if not isinstance(value, int):
            raise SchemaError(
                "maxLength value {0!r} is not an integer".format(value))
        return value

    @property
    def enum(self):
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



class Validator(object):
    """
    JSON Schema validator.
    """
    JSON_TYPE_MAP = {
        "string": basestring,
        "number": (int, float, decimal.Decimal),
        "integer": int,
        "object": dict,
        "array": list,
        "null": types.NoneType,
        "any": object
    }

    def validate_text(self, schema,  json_text):
        return self.validate(schema,json.loads(json_text))

    def validate(self, schema, obj):
        self._validate_type(schema, obj)
        if isinstance(obj, dict):
            self._validate_properties(schema, obj)
        return True

    def _validate_type(self, schema, obj):
        for json_type in schema.type:
            if isinstance(json_type, dict):
                self.validate(Schema(json_type), obj)
            if obj in (True, False) and json_type != "boolean":
                raise ValidationError(
                    "Object {obj!r} does not match type {type}".format(
                        obj = obj, type = json_type))
            else:
                if isinstance(obj, JSON_TYPE_MAP[json_type]):
                    # First one that matches, wins
                    break
        else:
            raise ValidationError(
                "Object {obj!r} does not match type {type}".format(
                    obj = obj, type = json_type))

    def _validate_properties(self, schema, obj):
        assert isinstance(obj, dict)
        for prop, prop_schema in schema.properties.iteritems():
            if prop in obj:
                return self.validate(Schema(prop_schema), obj[prop])
            else:
                if not prop_schema.optional:
                    raise ValidationError(
                        "Required property {prop!r} not found in {obj!r}".format(
                            obj = obj, prop = prop))


    def _validate_additional_properties(self, schema, obj):
        assert isinstance(obj, dict)
        additional_schema = self.schema.get("additionalProperties", {})
        if schema.additional_schema == False:
            # Additional properties are disallowed
            # Report exception for each unknown property
            for prop in obj.iterkeys():
                if prop not in schema.properties:
                    raise ValidationError(
                        "Unknown property {prop!r} found while "
                        "additionalProperties is false".format(
                            prop = prop))
        else:
            additional_schema = Schema(schema.additionalProperties)
            for prop, prop_value in obj.iteritems(): 
                self.validate(additional_schema, prop_value)


def validate(schema, data):
    """
    Validate specified JSON text (data) with specified schema

    Both schema and data must be strings
    """
    import simplejson as json
    return Validator.validate(
        Schema(json.loads(schema)),
        json.loads(data))
