# Foca Odoo 13.0 CE

## Clone

`git clone --recurse-submodules --branch 13.0 https://github.com/Foca-Software/addons-custom-foca.git`

## .conf File

This file is for reference of how is the `odoo.conf` addons path is configured in production.

## requirements.txt

This file has all the python packages using in production. It has the Odoo dependencies as well.

Useful to create a new python environment for development purposes.

Consider to add there if a module has new dependencies.

`pip3 install -r requirements.txt`
