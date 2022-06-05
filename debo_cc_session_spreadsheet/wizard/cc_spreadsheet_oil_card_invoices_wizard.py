from odoo import fields, models


class CashControlSpreadsheetOilCardInvoicesWizard(models.TransientModel):
    _name = "cc.spreadsheet.oil.card.invoices.wizard"
    _description = "Cash Control Spreadsheet Oil Card Invoices Wizard"

    def _default_oil_card_invoices_lines(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.invoice_ids.filtered(lambda i: i.oil_card_number is not False)
        )

    session_oil_card_invoice_ids = fields.Many2many(
        "account.move",
        relation="cc_spreadsheet_oil_card_invoice_wizard_rel",
        string="Oil Card Invoices",
        required=True,
        ondelete="cascade",
        default=_default_oil_card_invoices_lines,
    )

    def confirm_oil_card_invoices(self):
        return True
