# pylint: disable=protected-access
from odoo import fields, models

REC_CHECK = "account_check.account_payment_method_received_third_check"


class CashControlSpreadsheetChecksWizard(models.TransientModel):
    _name = "cc.spreadsheet.checks.wizard"
    _description = "Cash Control Spreadsheet Checks Wizard"

    def _default_check_lines(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.payment_ids.filtered(
                lambda p: p.journal_id.inbound_payment_method_ids
                == self.env.ref(REC_CHECK)
            )
            .mapped("check_ids")
        )

    session_check_ids = fields.Many2many(
        "account.check",
        relation="cc_spreadsheet_checks_wizard_rel",
        string="Checks",
        required=True,
        ondelete="cascade",
        default=_default_check_lines,
    )

    def confirm_checks(self):
        return True
