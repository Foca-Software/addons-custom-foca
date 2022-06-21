from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    planilla = fields.Char()

    config_type = fields.Many2one(related="config_id.type_id", string="Cashbox Type")

    config_uses_complement_invoice = fields.Boolean(related="config_type.uses_complement_invoice")

    total_liters = fields.Float(compute="_compute_total_liters")

    @api.depends("invoice_line_ids")
    def _compute_total_liters(self):
        for move in self:
            if move.invoice_line_ids:
                move.total_liters = sum(
                    [
                        move.mapped("invoice_line_ids")
                        .filtered(lambda l: l.product_id.is_fuel)
                        .mapped("quantity")
                    ]
                )
            else:
                move.total_liters = False

    @api.onchange("planilla")
    def _onchange_planilla(self):
        # session_id_debo is related so we need a new editable field to change cash_control_session_id
        if self.planilla:
            session_obj = self.env["cash.control.session"]
            session_id = session_obj.get_session_by_id_debo(self.planilla)
            # self.cash_control_session_id = session_id
            self.update({'cash_control_session_id': session_id})
