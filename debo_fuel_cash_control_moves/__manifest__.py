# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Fuel Station Cash Control Moves",
    "summary": """
        Create transfer between cash journals to Credit or Debit Card or Banks Journals
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["marcooegg"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sales",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ["base","debo_cash_control","debo_fuel_tanks","account_check"],
    ### XML Data files
    'data': [
        'wizards/res_config_settings.xml'
    ],
}
