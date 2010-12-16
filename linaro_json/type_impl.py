import datetime
import decimal


class DocumentPropertyType(object):

    def __init__(self, **kwargs):
        pass

    def get_initial_value(self):
        return None

    def to_json(self, python_value):
        return python_value


class BooleanType(DocumentPropertyType):

    def to_json(self, python_value):
        return bool(python_value)


class IntegerType(DocumentPropertyType):

    def to_json(self, python_value):
        return int(python_value)


class NumberType(DocumentPropertyType):

    def to_json(self, python_value):
        if isinstance(python_value, (int, float, decimal.Decimal)):
            return float(python_value)
        else:
            raise ValueError(
                "Unable to convert %r to JSON number" % python_value)


class StringType(DocumentPropertyType):

    def __init__(self, **kwargs):
        self._format = kwargs.get('format')

    def to_json(self, python_value):
        if self._format == 'date-time':
            if isinstance(python_value, datetime.datetime):
                return python_value.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                raise ValueError(
                    "Unable to format %r as date-time" % python_value)
        elif self._format is None:
            return unicode(python_value)
        else:
            raise NotImplementedError


class ObjectType(DocumentPropertyType):

    def to_json(self, python_value):
        return python_value.to_json()


class ArrayType(DocumentPropertyType):

    def get_initial_value(self):
        return []

    def to_json(self, python_value):
        return [item.to_json() for item in python_value]


class AnyType(DocumentPropertyType):
    pass


TYPE_MAP = {
    'boolean': BooleanType,
    'integer': IntegerType,
    'number': NumberType,
    'string': StringType,
    'object': ObjectType,
    'array': ArrayType,
    'any': AnyType,
}
