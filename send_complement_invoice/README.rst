=======================
Send Complement Invoice
=======================
.. |badge1| image:: https://img.shields.io/badge/maturity-Stable-brightgreen
    :target: https://odoo-community.org/page/development-status
    :alt: Stable
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-calyx--servicios%2Fcalyx-lightgray.png?logo=github
    :target: https://github.com/calyx-servicios/calyx.git
    :alt: calyx-servicios/calyx.git

|badge1| |badge2| |badge3|

This module extends the functionality of Complment Invoice to support configuration integration with Debo


Configure
=========

Go to Settings
Make sure that Debo Integration Fields URL is correct

Usage
=====

1. Every time a Complement Invoice is edited/created. Data will be sent to Debo's endpoint
Known issues / Roadmap
======================

* Data may be sent several times per record. In that case, all but the last should be discarded since this one is the complete record

Bug Tracker
===========

* Help Contact

Credits
=======

Authors
~~~~~~~

* Calyx Servicios S.A.

Contributors
~~~~~~~~~~~~

* `Calyx Servicios S.A. <https://odoo.calyx-cloud.com.ar/>`_
  
  * Marco Oegg
  * Federico Gregori

Maintainers
~~~~~~~~~~~

This module is maintained by Calyx Servicios S.A.

.. image:: https://ss-static-01.esmsv.com/id/13290/galeriaimagenes/obtenerimagen/?width=120&height=40&id=sitio_logo&ultimaModificacion=2020-05-25+21%3A45%3A05
   :alt: Calyx Servicios S.A.
   :target: https://odoo.calyx-cloud.com.ar/

CALYX SERVICIOS S.A. is part of the PGK Consultores economic group, member of an important global network, a world organization.
The PGK Consultores group is one of the 20 largest consultant-studios in Argentina with nearly 300 professionals.

This module is part of the `Odoo Foca <https://github.com/Foca-Software/addons-custom-foca>`_ project on GitHub.