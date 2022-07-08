# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    ###########################
    # Delete all the commented lines after editing the module
    ###########################
    "name": "Store Dependant Fields",
    "summary": """
        Add customizability of fields dependant on store
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    # any module necessary for this one to work correctly
    "depends": ["base","base_multi_store","product","cash_control"],
    ### XML Data files
    "data": [
        "security/ir.model.access.csv",
        "views/product_product.xml",
        "views/cash_control_config.xml",
    ],
    ### XML Demo files
    # only loaded in demo mode
    # "demo": [
    #     "demo/demo.xml",
    # ],
    ###########################
    # Delete all the commented lines after editing the module
    ###########################
}
