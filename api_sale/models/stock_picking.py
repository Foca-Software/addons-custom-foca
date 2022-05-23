from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"


    is_other_oil_sale_move = fields.Boolean(string="Is other Oil Card move")

    oil_card_number = fields.Char(string="Oil Card")

    sale_cc_session_id = fields.Many2one(
        comodel_name="cash.control.session",
        string="Sale Cash Control Session",
        related="sale_id.cash_control_session_id",
        store=True,
        readonly = False,
    )

    cash_control_session_id = fields.Many2one(
        comodel_name="cash.control.session",
        string="Cash Control Session",
        compute= "_compute_cc_session_id",
        store=True,
        readonly = False,
    )

    def _compute_cc_session_id(self) -> int:
        for picking in self:
            if picking.sale_id:
                picking.cash_control_session_id = picking.sale_id.cash_control_session_id
            elif picking.is_other_oil_sale_move:
                picking.cash_control_session_id = picking.cash_control_session_id or False
            else:
                picking.cash_control_session_id = False
                
