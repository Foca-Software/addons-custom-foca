# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Cash Control Type",
    "summary": """
        Add configurable types to Cash Control Config
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sale",
    "version": "13.0.0.0.1",
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["base","cash_control_extension","fuel_tanks_cash_control"],
    "data": [
        "security/ir.model.access.csv",
        "views/cash_control_config.xml",
        "views/cash_control_config_type.xml",
    ],
}
