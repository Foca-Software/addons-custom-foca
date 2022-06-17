from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.depends("transaction_type_cc_select")
    def _compute_sign_amount(self):
        for rec in self:
            if rec.transaction_type_cc_select == "TRANSFER_OUT":
                if rec.amount > 0:
                    rec.amount = -rec.amount
            else:
                rec.amount = abs(rec.amount)

    amount_sign = fields.Boolean(compute="_compute_sign_amount", store=True)

    def _transaction_type_cc_select_vals(self):
        return [
            ("TRANSFER_OUT", _("Outcome")),
            ("TRANSFER_IN", _("Income")),
        ]

    transaction_type_cc_select = fields.Selection(
        selection=_transaction_type_cc_select_vals,
        string="Transaction Type",
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.transaction_type in [
            value[0] for value in self._transaction_type_cc_select_vals()
        ]:
            _logger.info(self.with_user(1)._fields['transaction_type_cc_select'].selection)
            res.transaction_type_cc_select = res.transaction_type
        return res
