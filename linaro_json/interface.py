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
This module defines :class:`IFundamentalJSONType`,
:class:`ISimpleJSONType` and :class:`IComplexJSONType`.

All those interfaces can be used with the custom encoder and decoder
classes (:class:`PluggableJSONEncoder` and :class:`PluggableJSONDecoder`
respectively) to store arbitrary objects. Some operations require global
type awareness and type registration. This is performed by
:class:`ClassRegistry` class. A default instance called
:data:`DefaultClassRegistry` is provided when no special constraints are
required.
"""


class IFundamentalJSONType(object):
    """
    JSON fundamental type extension interface.

    This is a special-purpose extension currently only suitable to
    serialize numeric values without converting them to float or int.
    """

    def to_raw_json(self):
        """
        Return raw JSON encoding of the object.

        This method must return a generator yielding subsequent
        components of the final document. No syntax checking is
        perform (if you output gibberish you'll get a broken document)
        """
        raise NotImplementedError(self.to_raw_json)

    @classmethod
    def from_json(cls, json_doc):
        """
        Recreate the object based on a JSON document.

        The document contains whatever to_raw_json() returned (as long
        as it can be parsed back in one go).

        Note: When used with numeric types it will _not_ work. Instead
        the numeric type will be parsed using global numeric type parser
        (which defaults to float). This method is here just for
        completeness. If you want to change how numbers are parsed use
        float_parser argument on the JSONDecoder constructor.
        """
        raise NotImplementedError(cls.from_json)


class ISimpleJSONType(object):
    """
    JSON type extension for python types that can be stored
    as a string.

    This is a generic type extension that is safe to use and will not
    break the JSON document if used inappropriately. You can use this
    extension if you want to serialize something that is not really an
    object _or_ when mapping it to a dictionary with properties would
    look odd and verbose.
    """

    def to_json(self):
        """
        Serialize object to a python string.
        """
        raise NotImplementedError(self.to_json)

    @classmethod
    def from_json(cls, json_doc):
        """
        Recreate the object based on a python string.
        """
        raise NotImplementedError(cls.from_json)


class IComplexJSONType(ISimpleJSONType):
    """
    JSON type extension for python types that can be stored
    as a JSON dictionary. This extension is powerful enough
    to store arbitrary objects.

    For example on how to use this class check the .pod module
    """

    @classmethod
    def get_json_class_name(cls):
        """
        Return the class name hint that will be stored inside JSON
        dictionaries as a hint for the de-serializer.
        """
        raise NotImplementedError(cls.get_json_class_name)

    @classmethod
    def get_json_attr_types(cls):
        """
        Return type hinting for decoding this object's attributes.

        Note: this method is only required for de-serializing data
        using static type declarations.

        Hint is a dictionary of attributes mapping to type expressions.
        The following type expressions are defined:

            TYPE::
                Decode this attribute using TYPE which must be a
                :class:`IComplexJSONType` or :class:`ISimpleJSONType` or
                must have a proxy that maps it to one of those.
            [expr]::
                Decode this attribute as a list of objects where
                each object is of type ``expr``
            {ATTR: expr}::
                Decode this attribute as a dictionary where specified
                ATTR should be decoded with expr. You can add as many
                attributes as you like.

        Missing attributes are not converted in any special way and
        retain their original (string / number / list / dict) type.
        """
        raise NotImplementedError(cls.get_json_attr_types)

    def to_json(self):
        """
        Serialize object to a python dictionary.
        """
        raise NotImplementedError(self.to_json)

    @classmethod
    def from_json(cls, json_doc):
        """
        Recreate the object based on a python dictionary.
        """
        raise NotImplementedError(cls.from_json)


class IDocumentProperty(object):
    """
    JSON builder property interface.

    The property is a data descriptor providing access to the actual
    python data stored in the built document. The data is stored in
    actual instances of builder.Object (as dictionary members) and
    builder.Array (as list items). The property has no actual storage
    for that.

    The key ability is to be able to convert the data to the JSON
    equivalent if needed. This is performed by to_json()

    The actual data descriptor is implemented once, in a canonical way
    in builder.Property. It has to be synchronized with the
    implementation of builder.Object.
    """

    def to_json(self):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    def __set__(self, obj, python_value):
        raise NotImplementedError
