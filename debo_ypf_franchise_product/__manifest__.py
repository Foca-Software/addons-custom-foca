# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "YPF Franchise Products",
    "summary": """
        Add YPF Franchise specific fields and controls to Product
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "auto_install":True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["base","debo_ypf_franchise","product","account"],
    ### XML Data files
    "data": [
        "security/ir.model.access.csv",
        "views/account_tax.xml",
        "views/product_pricelist.xml",
        "views/product.xml",
        "views/ypf_product_category.xml",
    ],
}
