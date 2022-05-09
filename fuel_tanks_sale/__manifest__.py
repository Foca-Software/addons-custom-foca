# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fuel Tanks Sale",
    "summary": """
        Add sale related functionality to fuel tanks
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sale",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "depends": ["base","sale", "stock_fuel_tanks","sale_stock"],
    'data': [
        'views/sale_order.xml',
        'views/stock_picking.xml',
    ],
}
