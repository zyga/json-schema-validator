Version History
***************

Version 2.0
===========

* New major release, incompatible with past releases
* Drop everything apart from schema validator as other elements have lost their significance
* Tweak requirements to support current Ubuntu LTS (10.04 aka Lucid)
* Refresh installation instructions to point to the new PPA, provide links to
  lp.net project page and pypi project page.

Version 1.2.3
=============

* Change how setup.py finds the version of the code to make it pip install okay
  when simplejson is not installed yet. 

Version 1.2.2
=============

* Fix another problem with pip and versiontools (removed unconditional import
  of versiontools from __init__.py)

Version 1.2.1
=============

* Fix installation problem with pip due to versiontools not being available
  when parsing initial setup.py

Version 1.2
===========

* Change name to linaro-json
* Add dependency on versiontools
* Register on pypi
* Add ReST documentation


Version 1.1
===========

* Add support for retrieving default values from the schema


Version 1.0
===========

* Initial release
