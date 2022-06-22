from odoo import fields, models


class CashControlSpreadsheetCardsDetailsWizard(models.TransientModel):
    _name = "cc.spreadsheet.cards.details.wizard"
    _description = "Cash Control Spreadsheet Cards Details Wizard"

    def _default_cards_details_lines(self):
        payments_ids = (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.payment_ids.filtered(lambda p: p.card_id)
        )

        vals_list = []
        for payment in payments_ids:
            card = {}

            card["card_number"] = payment.card_number
            card["amount"] = payment.amount
            card["payment_ref"] = payment.payment_group_id.id
            card["invoice_ref"] = payment.communication
            card["date"] = payment.payment_date
            # This is misspelled in the original code ↓
            card["ticket_number"] = payment.tiket_number

            vals_list.append(card)

        cards = self.env["cc.spreadsheet.cards.details.line"].create(vals_list)
        return cards

    session_cards_details_ids = fields.Many2many(
        "cc.spreadsheet.cards.details.line",
        relation="cc_spreadsheet_cards_details_line_wizard_rel",
        string="Cards Details",
        required=True,
        ondelete="cascade",
        default=_default_cards_details_lines,
    )

    def confirm_cards_details(self):
        return True


class CashControlSpreadsheetCardsDetailsLineWizard(models.TransientModel):
    _name = "cc.spreadsheet.cards.details.line"
    _description = "Cash Control Spreadsheet Cards Details Line Wizard"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True
    )
    card_number = fields.Char()
    amount = fields.Monetary(
        currency_field="company_currency_id",
    )
    ticket_number = fields.Char()
    payment_ref = fields.Many2one(
        "account.payment.group",
        string="Payment Reference",
        readonly=True,
    )
    invoice_ref = fields.Char(string="Invoice Reference", required=True)
    date = fields.Date(required=True)
