# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{

    "name": "Debo Contact Fields",
    "summary": """
        It extends the partner/client fields.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["lucianobaleani"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ["base", "contacts","send_debo_fields"],

    'data': [
        'views/partner_views_inherit.xml',
    ],
}
