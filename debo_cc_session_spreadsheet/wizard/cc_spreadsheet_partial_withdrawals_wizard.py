# pylint: disable=protected-access
from odoo import fields, models


class CashControlSpreadsheetPartialWithdrawalsWizard(models.TransientModel):
    _name = "cc.spreadsheet.partial.withdrawals.wizard"
    _description = "Cash Control Spreadsheet Partial Withdrawals Wizard"

    def _domain_partial_withdrawals_lines(self):
        # Get session of the spreadsheet
        active_ids = self._context.get("active_ids")
        if not active_ids:
            return []
        session_id = (
            self.env["cash.control.session.spreadsheet"].browse(active_ids).session_id
        )
        # Get statement_id from the session
        statement_id = session_id.statement_id.id
        # Get lines from statement_id of the session
        return [("statement_id", "=", statement_id), ("ref", "!=", False)]

    def _default_partial_withdrawals_lines(self):
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
        domain=_domain_partial_withdrawals_lines,
        default=_default_partial_withdrawals_lines,
    )

    def _default_session_config_id_name(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.config_id.name
        )

    session_config_id_name = fields.Char(
        default=_default_session_config_id_name,
    )

    def _default_spreadsheet_state(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .state
        )

    session_state = fields.Char(
        default=_default_spreadsheet_state,
    )

    def _default_session_bank_statement_id(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.statement_ids.filtered(lambda s: s.journal_id.code == "TESO")
        )

    session_bank_statement_id = fields.Many2one(
        "account.bank.statement",
        default=_default_session_bank_statement_id,
    )

    def confirm_withdrawals(self):
        active_ids = self._context.get("active_ids")
        spreadsheet_id = self.env["cash.control.session.spreadsheet"].browse(active_ids)
        session_id = spreadsheet_id.session_id

        # Update withdrawal lines
        for transfer in session_id.transfer_ids.filtered(
            lambda t: t.id not in self.session_transfer_ids.ids
        ):
            statement = transfer.statement_id
            statement.write({"state": "open"})
            transfer.button_cancel_reconciliation()
            transfer.unlink()
            statement.write({"state": "confirm"})

        # Update cash amount
        spreadsheet_id._compute_cash()

        return True
