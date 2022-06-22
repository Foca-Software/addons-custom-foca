from odoo import fields, models, api


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.depends("transaction_type_cc_select")
    def _compute_sign_amount(self):
        for rec in self:
            if rec.transaction_type_cc_select == "TRANSFER_OUT":
                if rec.amount > 0:
                    rec.amount_sign = -rec.amount
            else:
                rec.amount_sign = abs(rec.amount)

    amount_sign = fields.Boolean(compute="_compute_sign_amount", store=True)

    transaction_type_cc_select = fields.Selection(
        [
            ("TRANSFER_OUT", "Outcome"),
            ("TRANSFER_IN", "Income"),
        ],
        string="Transaction Type",
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.transaction_type_cc_select:
            res.transaction_type = res.transaction_type_cc_select
        return res
