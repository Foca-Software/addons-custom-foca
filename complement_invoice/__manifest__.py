# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Complement Invoice",
    "summary": """
        Allow creation of Complement invoice according to Debo specifications
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Alpha",
    "version": "13.0.1.0.0",
    # see https://odoo-community.org/page/development-status
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    # any module necessary for this one to work correctly
    "depends": ["base","cash_control_type","debo_fuel_tanks"],
    ### XML Data files
    # "data": [
    #     "security/ir.model.access.csv",
    #     "views/views.xml",
    #     "views/templates.xml",
    # ],
    ### XML Demo files
    # only loaded in demo mode
    # "demo": [
    #     "demo/demo.xml",
    # ],
    ###########################
    # Delete all the commented lines after editing the module
    ###########################
}
