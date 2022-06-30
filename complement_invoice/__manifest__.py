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
    "version": "13.0.0.0.1",
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    # any module necessary for this one to work correctly
    "depends": ["base","cash_control_type","debo_fuel_tanks", "account","send_debo_fields"],
    "data": [
        "data/add_script.xml",
        "security/ir.model.access.csv",
        "views/cash_control_config_type.xml",
        "views/complement_invoice_config.xml",
        "views/complement_invoice_config_line.xml",
        "views/res_partner.xml",
    ],
}
