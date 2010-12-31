"""
JSON document API.

Allows to construct set of python classes that act as a schema and save
them to pure JSON structures
"""

from linaro_json.interface import IDocumentProperty
from linaro_json.type_impl import TYPE_MAP


class _DocumentMetaData(object):
    """
    Helper class for storing meta-data about a document schema.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _DocumentMeta(type):
    """
    Meta class for JSON Document objects.

    It cooperates with JSON Document Properties and builds a list of
    properties stored in the meta-data helper object accessible as
    cls._meta.props. In addition all property names are stored as
    a frozenset in cls._meta.prop_name_set.
    """

    def __new__(cls, name, bases, dct):
        props = []
        for prop_name, prop in dct.iteritems():
            if isinstance(prop, IDocumentProperty):
                if prop.name is None:
                    prop.name = prop_name
                props.append(prop)
        props.sort(key=lambda prop: prop._sequence_number)
        dct['_meta'] = _DocumentMetaData(
            props=props,
            prop_name_set=frozenset([prop.name for prop in props])
        )
        return type.__new__(cls, name, bases, dct)


class DocumentObject(object):
    """
    JSON Document Object.

    Corresponds to JSON object { }. May have any number of JSON Document
    Properties.

    The live python value of each property is stored. The entire
    document can be converted to JSON with the to_json() method.
    """
    __metaclass__ = _DocumentMeta

    def __init__(self, **kwargs):
        self._fields = {}
        if "_template" in kwargs:
            template = kwargs['_template']
            del kwargs["_template"]
        else:
            template = None
        for prop in self._meta.props:
            if prop.name not in kwargs:
                if template:
                    value = template._get_initial_value_for_property(prop)
                else:
                    value = prop._get_initial_value()
            else:
                value = kwargs[prop.name]
            if value is None:
                continue
            setattr(self, prop.name, value)
        for prop_name in kwargs.iterkeys():
            if prop_name not in self._meta.prop_name_set:
                raise ValueError(
                    "%r does not have property %r" % (self, prop_name))

    def to_json(self):
        """
        Convert this object to JSON.

        The returned value has no connection to the document. It can be
        safely pickled, manipulated etc. The original document can be
        discarded if no longer necessary.
        """
        return dict([
            (prop.name, prop.to_json(self._fields[prop.name]))
            for prop in self._meta.props
            if prop.name in self._fields
        ])


class DocumentProperty(IDocumentProperty):
    """
    JSON document property.

    Corresponds to properties on JSON object. Document properties may
    carry a number of attributes that are defined by the JSON schema.
    Currently most of those are unused and just stored. In the future
    they can be used to generate a full schema of the document based
    purely on the python class model.

    Internally the most important attribute is the type attribute. It
    is used to select type implementation that in turn defines how the
    property behaves.

    Internally this class knows about the implementation detail of
    DocumentObject to store/retrieve the actual property value from the
    parent document.
    """

    _valid_attrs = frozenset([
        "additionalProperties",
        "description",
        "enum",
        "format",
        "optional",
        "requires",
        "type",
        "items",
    ])

    _sequence_number = 0

    def __init__(self, **kwargs):
        self.__dict__['_sequence_number'] = self.__class__._sequence_number
        self.__class__._sequence_number += 1
        for name in kwargs.iterkeys():
            if name not in self._valid_attrs:
                raise ValueError("Invalid DocumentProperty initializer: %r" % name)
        self._type_impl = TYPE_MAP[kwargs.get("type", "any")](
            format=kwargs.get("format"))
        self.name = None # Name needs a default value for DocumentMeta
        self.__dict__.update(kwargs)
        self.__doc__ = kwargs.get('description')
        self.__doc__ += "\n\nJSON attributes:\n"
        for attr in self._valid_attrs:
            if attr in kwargs:
                self.__doc__ += "\t%s: %s\n" % (attr, kwargs[attr])

    def to_json(self, python_value):
        """
        Convert this property to JSON
        """
        return self._type_impl.to_json(python_value)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.name not in obj._fields:
            raise AttributeError("%r object has no attribute %r" % (
                type(obj).__name__, self.name))
        return obj._fields[self.name]

    def __set__(self, obj, python_value):
        obj._fields[self.name] = python_value

    def _get_initial_value(self):
        if hasattr(self, "default"):
            return self.default
        return self._type_impl.get_initial_value()


class DocumentTemplate(object):
    """
    Document templates are a simple way to construct new objects and
    being able to define custom defaults.

    A template may have any number of properties or class variables that
    have a value. Any value not specified in the DocumentObject
    constructor that also exists in the DocumentTemplate will be used to
    initialize appropriate DocumentProperties.

    The logic for doing this is inside the DocumentObject constructuror.
    It calls the internal implementation method of this class to obtain
    the default value.
    """

    def _get_initial_value_for_property(self, prop):
        return getattr(self, prop.name, prop._get_initial_value())


class DocumentBuilder(object):
    """
    Document builder is a joining point for DocumentObject and
    DocumentTemplate. The builder instance is callable and will use any
    available templates to instantiate the DocumentObjects.

    It's a simple way to build objects using a common schema and using
    arbitrary default values at the same time.
    """

    def __init__(self, *templates):
        self.templates = templates

    def __call__(self, schema_cls, **kwargs):
        """
        Construct an instance of schema_cls (DocumentObject) using any
        known templates registered in DocumentBuilder.__init__().

        All additional arguments are passed to the constructor and take
        precedence over defaults (including defaults from the template
        and defaults from the type itself)
        """
        for template_cls in self.templates:
            if template_cls.__schema__ is schema_cls:
                kwargs["_template"] = template_cls()
                break
        return schema_cls(**kwargs)
