# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Send DEBO Fields",
    "summary": """
        Add capability to send data to DEBO db.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Endpoint",
    "version": "13.0.0.0.2",
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
        "contacts",
        "product",
        "debo_integration_fields",
    ],
    "data": [
        "views/res_config.xml",
        "views/res_partner.xml",
        "views/product_product.xml",
        "views/product_pricelist.xml",
    ],
}
