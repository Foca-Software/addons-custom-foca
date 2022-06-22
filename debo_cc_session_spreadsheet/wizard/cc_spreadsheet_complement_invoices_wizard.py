from odoo import fields, models


class CashControlSpreadsheetComplementInvoicesWizard(models.TransientModel):
    _name = "cc.spreadsheet.complement.invoices.wizard"
    _description = "Cash Control Spreadsheet Complement Invoices Wizard"

    def _default_complement_invoice_lines(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.complement_invoice_ids
        )

    session_complement_invoice_ids = fields.Many2many(
        "account.move",
        relation="cc_spreadsheet_complement_invoices_wizard_rel",
        string="Complement Invoices",
        required=True,
        ondelete="cascade",
        default=_default_complement_invoice_lines,
    )

    def confirm_complement_invoices(self):
        return True
