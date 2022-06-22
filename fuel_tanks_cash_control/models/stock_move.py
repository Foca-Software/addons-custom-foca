from email.policy import default
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    cash_control_session_id = fields.Many2one(
        comodel_name="cash.control.session",
        string="Session",
        related="picking_id.cash_control_session_id",
    )
