# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Fuel Tanks",
    "summary": """
       Manage fuel tanks like locations
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
        "stock",
        "product",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/stock_location.xml",
        "views/sale_order.xml",
        "views/stock_pump.xml",
    ],
}
