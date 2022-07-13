# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DEBO Api Cashbox Integration",
    "summary": """
        Open and Close Cash_control Sessions through API requests.
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
        "debo_fuel_tanks",
        "fuel_tanks_cash_control",
        "debo_sector",
    ],
    "data": [
        "views/cash_control_config.xml",
        "views/cash_control_session.xml",
    ],
}
