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
    
    @api.depends("config_type")
    @api.constrains("debo_transaction_type")
    def _constraint_config_type_debo_transaction_type(self):
        self.planilla = self.planilla
        _logger.info(self.planilla)
        if (
            self.debo_transaction_type == "complement"
            and not self.config_uses_complement_invoice
        ):
            _logger.error(self.config_uses_complement_invoice)
            raise ValidationError(
                "You cannot create Complement Invoices in that Cashbox"
            )

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

    # @api.constrains("total_liters")
    # def _constraint_total_liters(self):
    #     """Does not allow creation of Complement Invoices to Anonymous Consumer where
    #     total fuel liters exceeds config type's restriction

    #     Raises:
    #         ValidationError: Invoice exceeds max liter amount
    #     """
    #     if (
    #         self.debo_transaction_type == "complement"
    #         and self.partner_id == self.env.ref("l10n_ar.par_cfa")
    #         and self.config_type.ci_restricts_liters
    #         and self.total_liters > self.config_type.ci_liter_max_amount
    #     ):
    #         raise ValidationError("Invoice exceeds max liter amount")


    @api.onchange("planilla")
    def _onchange_planilla(self):
        # session_id_debo is computed so we need a new editable field to change cash_control_session_id
        if self.planilla:
            session_obj = self.env["cash.control.session"]
            session_id = session_obj.get_session_by_id_debo(self.planilla)
            self.cash_control_session_id = session_id

    @api.constrains("planilla", "cash_control_session_id")
    def constraint_planilla_not_found(self):
        if self.planilla and not self.cash_control_session_id:
            raise ValidationError(_("Session not found with that planilla"))

    # TODO: This fields do not exist yet. Constraint should apply
    # @api.constrains("amount_total", "config_type")
    # def _constraint_config_type_max_min_amount(self):
    #     if self.debo_transaction_type == "complement" and (
    #         (
    #             self.partner_id.ci_maximum_amount
    #             and self.amount_total > self.partner_id.ci_maximum_amount
    #         )
    #         or 
    #         (
    #             self.partner_id.ci_minimum_amount
    #             and self.amount_total < self.partner_id.ci_minimum_amount
    #         )
    #     ):
    #         raise ValidationError(
    #             "Total amount exceeds maximum amount or is less than minimum amount"
    #         )

