# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Sector",
    "summary": """
        Implement Sector concept in odoo for integration
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
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["base","stock","cash_control_extension",],
    ### XML Data files
    "data": [
        "security/ir.model.access.csv",
        "views/sector_sector.xml",
        "views/stock_warehouse.xml",
        "views/product.xml",
        "views/cc_config.xml",
    ],
}
