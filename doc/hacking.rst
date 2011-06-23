
Hacking
*******

The project is hosted on github
(http://github.com/zyga/json-schema-validator/), feel free to fork it and
propose a pull request.

Goals
-----

The goal of this project is to construct a complete and fast implementation of the
JSON Schema as defined by http://json-schema.org/. 

JSON is powerful because of the simplicity.  Unlike the baroque YAML it thrives
on being easy to implement in any language, correctly, completely, with
confidence and test. Python has a good built-in implementation of the
serializer (decoder and encoder) but lacks more advanced tools. Working with
JSON as a backend for your application, whether it's configuration, application
data or envelope for your RPC system, almost always requires data validation
and integrity checking.

Infrastructure
--------------

Github is used for:

* Hosting source code (in git)
* Reporting and tracking bugs

Launchpad.net is used for:

* Hosting source code (as bzr mirror)
* Packaging aid for Ubuntu

PyPi is used for:

* Hosting released tarballs
* Hosting built documentation
