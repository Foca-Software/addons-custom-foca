from odoo import fields, models, api


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

    # def _transaction_type_cc_select_vals(self):
    #     return [
    #         ("TRANSFER_OUT", "Outcome"),
    #         ("TRANSFER_IN", "Income"),
    #     ]

    # transaction_type_cc_select = fields.Selection(
    #     _transaction_type_cc_select_vals,
    #     string="Transaction Type",
    # )

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     possible_vals = [val[0] for val in self._transaction_type_cc_select_vals()]
    #     if res.transaction_type in possible_vals:
    #         res.transaction_type_cc_select = res.transaction_type
    #     return res

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
        possible_vals = [
            val[0]
            for val in self.sudo()._fields["transaction_type_cc_select"].selection
        ]
        if res.transaction_type in possible_vals:
            res.transaction_type_cc_select = res.transaction_type
        return res
