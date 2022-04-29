from odoo import models, fields


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    id_debo = fields.Char(string="Spreadsheet")
