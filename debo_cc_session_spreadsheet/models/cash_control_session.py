from odoo import models, _
from odoo.exceptions import UserError


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    def _create_cash_control_session_spreadsheet(self, spreadsheets):
        return spreadsheets.create(
            {
                "session_id": self.id,
                "cash_amount_start": self.statement_balance_start,
                "cash_amount_end": self.statement_balance_end_real,
                "checking_account_invoices_amount": self.checking_account_invoices_amount,
            }
        )

    def action_cash_control_session_spreadsheet(self):
        """
        Button action to create/open the cash control session spreadsheet view
        and redirect the user to it.
        """
        self.ensure_one()

        if not self.id_debo:
            raise UserError(_("Cash control session must have an id_debo"))

        spreadsheets = self.env["cash.control.session.spreadsheet"]

        spreadsheet = spreadsheets.search([("session_id", "=", self.id)])
        if not spreadsheet:
            spreadsheet = self._create_cash_control_session_spreadsheet(spreadsheets)

        if self.state == "closed":
            self.update({"state": "spreadsheet_control"})

        return {
            "type": "ir.actions.act_window",
            "res_model": "cash.control.session.spreadsheet",
            "view_mode": "form",
            "target": "current",
            "res_id": spreadsheet.id,
        }
