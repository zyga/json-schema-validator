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


"""Unit tests for new validation engine."""

from __future__ import absolute_import, print_function

try:
    from unittest2 import TestCase
except:
    from unittest import TestCase

from json_schema_validator.engine import Validator as V
from json_schema_validator.engine import TypeFragment
from json_schema_validator.errors import SchemaError
from json_schema_validator.errors import ValidationError


# NOTE: Tests use the following special constants:
#
# "foo" - for some arbitrary string
# 42 - for some arbitrary integer
# 3.14 - for some arbitrary floating point number


class TypeFragmentTests(TestCase):

    def test_unknown_type(self):
        with self.assertRaisesRegex(SchemaError, "unsupported") as raised:
            TypeFragment({"type": "my-type"})
        self.assertEqual(raised.exception.schema, {"type": "my-type"})

    def test_invalid_type_kind(self):
        for js_type in [42, 3.14, False, {}]:
            with self.subTest(js_type=js_type):
                with self.assertRaisesRegex(SchemaError, "kind") as raised:
                    TypeFragment({"type": js_type})
                self.assertEqual(raised.exception.schema, {"type": js_type})

    def test_union_type_too_short(self):
        for js_type in [], ['int']:
            with self.subTest(js_type=js_type):
                with self.assertRaisesRegex(SchemaError, "two") as raised:
                    TypeFragment({"type": js_type})
                self.assertEqual(raised.exception.schema, {"type": js_type})

    def test_simple_type(self):
        with self.subTest(js_type="string"):
            frag = TypeFragment({"type": "string"})
            frag.assertValid("foo")  # string
            frag.assertNotValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="number"):
            frag = TypeFragment({"type": "number"})
            frag.assertNotValid("foo")  # string
            frag.assertValid(42)  # number, integer
            frag.assertValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="integer"):
            frag = TypeFragment({"type": "integer"})
            frag.assertNotValid("foo")  # string
            frag.assertValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="boolean"):
            frag = TypeFragment({"type": "boolean"})
            frag.assertNotValid("foo")  # string
            frag.assertNotValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="object"):
            frag = TypeFragment({"type": "object"})
            frag.assertNotValid("foo")  # string
            frag.assertNotValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="array"):
            frag = TypeFragment({"type": "array"})
            frag.assertNotValid("foo")  # string
            frag.assertNotValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertValid([])  # array
            frag.assertNotValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="null"):
            frag = TypeFragment({"type": "null"})
            frag.assertNotValid("foo")  # string
            frag.assertNotValid(42)  # number, integer
            frag.assertNotValid(3.14)  # number
            frag.assertNotValid(True)  # boolean
            frag.assertNotValid({})  # object
            frag.assertNotValid([])  # array
            frag.assertValid(None)  # null
            frag.assertNotValid(object())  # any
        with self.subTest(js_type="any"):
            frag = TypeFragment({"type": "any"})
            frag.assertValid("foo")  # string
            frag.assertValid(42)  # number, integer
            frag.assertValid(3.14)  # number
            frag.assertValid(True)  # boolean
            frag.assertValid({})  # object
            frag.assertValid([])  # array
            frag.assertValid(None)  # null
            frag.assertValid(object())  # any

    def test_union_type(self):
        frag = TypeFragment({"type": ['string', 'number']})
        frag.assertValid("foo")  # string
        frag.assertValid(42)  # number, integer
        frag.assertValid(3.14)  # number
        frag.assertNotValid(True)  # boolean
        frag.assertNotValid({})  # object
        frag.assertNotValid([])  # array
        frag.assertNotValid(None)  # null
        frag.assertNotValid(object())  # any

    def test_any_optimized_out(self):
        for js_type in ['any', ['any', 'number'], ['any', 'null']]:
            with self.subTest(js_type=js_type):
                frag = TypeFragment({"type": js_type})
                self.assertEqual(len(list(frag.fast_cmds())), 0)

    def test_union_optimized(self):
        frag = TypeFragment({"type": ['string', 'number']})
        # Checking type union is just as fast as checking regular types
        self.assertEqual(len(list(frag.fast_cmds())), 1)


class ValidatorTests(TestCase):

    def test_smoke(self):
        self.assertTrue(V({"type": "number"})(1))
        self.assertTrue(V({"type": "number"})(1.5))
        with self.assertRaises(ValidationError) as raised:
            V({"type": "number"})("hi")
        self.assertEqual(
            raised.exception.new_message,
            "Object has incorrect type (expected number)")
        self.assertEqual(raised.exception.object_expr, "")
        self.assertEqual(raised.exception.schema_expr, "/type")
