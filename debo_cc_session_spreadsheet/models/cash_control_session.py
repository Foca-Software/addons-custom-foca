from odoo import models
from odoo.exceptions import UserError


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    def get_cash_sales_amount(self):
        """
        Return the total amount of sales in cash in the cash control session.
        """
        self.ensure_one()
        return sum(
            [line.amount for line in self.payment_ids if line.journal_id.type == "cash"]
        )

    def _create_cash_control_session_spreadsheet(self, Spreadsheets):
        cash_amount_sales = self.get_cash_sales_amount()
        return Spreadsheets.create(
            {
                "cash_control_session_id": self.id,
                "cash_amount_start": self.statement_balance_start,
                "cash_amount_sales": cash_amount_sales,
            }
        )

    def action_cash_control_session_spreadsheet(self):
        """
        Button action to create/open the cash control session spreadsheet view
        and redirect the user to it.
        """
        self.ensure_one()

        if not self.id_debo:
            raise UserError("Cash control session must have an id_debo")

        Spreadsheets = self.env["cash.control.session.spreadsheet"]

        spreadsheet = Spreadsheets.search([("cash_control_session_id", "=", self.id)])
        if not spreadsheet:
            spreadsheet = self._create_cash_control_session_spreadsheet(Spreadsheets)

        if self.state == "closed":
            self.update({"state": "spreadsheet_control"})

        return {
            "type": "ir.actions.act_window",
            "res_model": "cash.control.session.spreadsheet",
            "view_mode": "form",
            "target": "current",
            "res_id": spreadsheet.id,
        }
