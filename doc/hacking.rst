
Hacking
*******

Dear hackers.

The project is hosted on http://launchpad.net/linaro-python-json/ *and*
http://pypi.python.org/linaro-json/. There is a name difference, the canonical
name is ``linaro-json``. I cannot rename the project on launchpad so we'll have
to live with both.

Goals
-----

The goal of this project is to construct an universal collection of tools to
work with JSON documents in python.

JSON is powerful because of the simplicity.  Unlike the baroque YAML it thrives
on being easy to implement in any language, correctly, completely, with
confidence and test. Python has a good built-in implementation of the
serializer (decoder and encoder) but lacks more advanced tools. Working with
JSON as a backend for your application, whether it's configuration, application
data or envelope for your RPC system, almost always requires data validation
and integrity checking.

Infrastructure
--------------

Launchpad.net is used for:

* Hosting source code (in bzr)
* Reporting and tracking bugs
* Project management (release tracking, feature tracking, etc)

PyPi is used for:

* Hosting released tarballs
* Hosting built documentation
