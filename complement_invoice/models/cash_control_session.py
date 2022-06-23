from odoo import models, fields, api


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    turn_id = fields.Many2one(comodel_name="cash.control.turn", string="Turn")
