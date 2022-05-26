# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DEBO Integration Fields",
    "summary": """
        Add fields needed for integration.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Endpoint",
    "version": "13.0.1.0.1",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["base", "account", "contacts", "product", "sale", "cash_control","stock"],
    "data": [
        "views/account_move.xml",
        "views/id_debo_views.xml",
        "views/product_pricelist_item.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
}
