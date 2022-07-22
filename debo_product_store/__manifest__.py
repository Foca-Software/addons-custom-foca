# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Product Store",
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
    "depends": [
        "base",
        "account_multi_store",
        "sale_multi_store",
        "product",
        "debo_sector",
        "web_domain_field",
        "send_debo_fields",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/change_warehouse_wizard.xml",
        "wizards/enable_disable_product_wizard.xml",
        "views/product_product.xml",
        "wizards/actions.xml",
    ],
}
