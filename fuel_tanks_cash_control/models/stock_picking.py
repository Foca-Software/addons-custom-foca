from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cash_control_session_id = fields.Many2one(
        comodel_name="cash.control.session",
        string="Cash Control Session",
        related="sale_id.cash_control_session_id",
        store=True
    )
