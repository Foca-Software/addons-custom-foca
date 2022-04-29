from odoo import models, fields, api, _


class AccountTax(models.Model):
    _inherit = "account.tax"

    id_debo = fields.Char(string="ID_DEBO")
