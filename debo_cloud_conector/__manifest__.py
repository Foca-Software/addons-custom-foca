# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DEBO Cloud Connector",
    "summary": """
        Create moves through Json Request.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Endpoint",
    "version": "13.0.0.1.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "account",
        "contacts",
        "product",
        "cash_control",
        # "auth_jwt",
    ],
    "data": [
        # "data/auth_jwt_validator.xml",
        # "views/res_partner.xml",
        # "views/product_product.xml",
        "views/res_company.xml",
    ],
}
