# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Historical Price",
    "summary": """Add custom price for each partner""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["Oegg Marco"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sales",
    "version": "13.0.0.0.1",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'contacts',
        'sale',
    ],
    "data": [
        'views/res_partner.xml',
    ],
}
