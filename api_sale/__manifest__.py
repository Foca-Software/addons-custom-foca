# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DEBO Api Sale Integration",
    "summary": """
        Create Sales, Invoices and Pay them through API requests.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Endpoint",
    "version": "13.0.0.0.1",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "account",
        "cash_control_multi_store",
        "debo_fuel_tanks",
        "debo_integration_fields",
        "debo_sector",
    ],
    "data": [
        "data/account_journal_data.xml",
        "data/res_partner_data.xml"
    ],
}
