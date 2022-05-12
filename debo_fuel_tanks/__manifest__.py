# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Fuel Tanks",
    "summary": """
        Debo Specific modifications to Fuel Tanks
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Operations",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "depends": ["base", "fuel_tanks_sale", "fuel_tanks_cash_control"],
    "data": [
        "views/cash_control_session.xml",
        "views/sale_order.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
        "views/stock_pump_views.xml",
    ],
}
