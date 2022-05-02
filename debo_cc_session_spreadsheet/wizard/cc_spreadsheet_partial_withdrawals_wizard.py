from odoo import fields, models


class CashControlSpreadsheetPartialWithdrawalsWizard(models.TransientModel):
    _name = "cc.spreadsheet.partial.withdrawals.wizard"
    _description = "Cash Control Spreadsheet Partial Withdrawals Wizard"

    def _default_partial_withdrawals(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.transfer_ids
        )

    session_transfer_ids = fields.Many2many(
        "account.bank.statement.line",
        relation="cc_spreadsheet_partial_withdrawals_wizard_rel",
        string="Partial Withdrawals",
        required=True,
        ondelete="cascade",
        default=_default_partial_withdrawals,
    )
