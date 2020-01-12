[![Build Status](https://travis-ci.org/zyga/json-schema-validator.svg?branch=master)](https://travis-ci.org/zyga/json-schema-validator)

About
=====

This package contains an implementation of JSON Schema validator as defined by
http://json-schema.org/

Installation
============

$ pip install json-schema-validator

Testing
=======

You will need tox (get it from pip) as python2.7

$ tox

Generating Documentation
========================

Python package 'Sphinx' can be used to generate documentation for the module, giving details as to the mechanics of each module component, their subsequent classes and functions. To install sphinx use:
`pip3 install sphinx`

If you don't already have it, sphinx requires the 'versiontools' package which is not included in the install for sphinx itself. Install this with:
`pip3 install versiontools`

Now you can generate documentation. Navigate to the root of your json_schema_validator module directory (you can find this path by using: `pip3 show json_schema_validator`, the path will be under 'location in the output). From your shell (not the python interpreter) type `sphinx-build -html doc [dest]` (where [dest] is a directory name you would like to build your documentation to)

Once your documentation is built you will need to host it to see it. `cd` into the directory you used as '[dest]' and use `pydoc -p 8080`. Open your browser and type `pydoc -p 8080`


