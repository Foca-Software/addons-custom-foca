# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Cash Control - Stock Fuel Tanks",
    "summary": """
       Manage fuel transactions in cash control sessions
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Stock",
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
        "stock_fuel_tanks",
        "fuel_tanks_sale",
        "debo_integration_fields",  # TODO: Remove dependency
        "cash_control_extension",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/cash_control_session.xml",
        "views/stock_picking.xml",
    ],
}
