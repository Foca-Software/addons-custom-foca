# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Fuel Tanks History",
    "summary": """
        This module adds a history of the fuel tanks (pumps) used in Cash Control Sessions.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["FedericoGregori"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sales",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ["cash_control", "stock_fuel_tanks", "fuel_tanks_cash_control"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_pump.xml",
    ],
}
