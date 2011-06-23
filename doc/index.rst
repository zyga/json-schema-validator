JSON Schema Validator 
*********************

About
=====

This package contains an implementation of JSON Schema validator.

.. note::
    This project is just getting started. While the code relatively
    feature-complete, rather well tested and used in production daily the
    *documentation* is lacking.

.. warning::
    This implementation was based on the *second draft* of the specification
    A third draft was published on the 22nd Nov 2010. This draft introduced
    several important changes that are not yet implemented.

.. note::
    Only a subset of schema features are currently supported.
    Unsupported features are detected and raise a NotImplementedError
    when you call :func:`json_schema_validator.schema.Validator.validate`

.. seealso::
    http://json-schema.org/ for details about the schema

Table of contents
=================

.. toctree::
    :maxdepth: 2
    
    installation.rst
    usage.rst
    reference.rst
    changes.rst
    hacking.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

