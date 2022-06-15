from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    complement_invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="cash_control_session_id",
        string="Complement Invoices",
        domain=[("debo_transaction_type", "=", "complement"), ("state", "=", "posted")],
    )

    def invoice_ids_domain(self):
        return [
            ("debo_transaction_type", "=", "standard"),
            ("state", "=", "posted"),
            ("journal_id.type", "in", ["purchase", "sale"]),
        ]

    invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="cash_control_session_id",
        string="Invoices",
        domain=invoice_ids_domain,
    )

    card_batch_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="cash_control_session_id",
        string = "Card Batchs",
        domain = [('debo_transaction_type','=','card_batch'),('payment_type','=','transfer')]
    )

    register_check_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="cash_control_session_id",
        string = "Register Checks",
        domain = [('debo_transaction_type','=','register_check'),('payment_type','=','transfer')]
    )


class CashControlSessionPaymentSummary(models.Model):

    _inherit = "cash.control.session.payment_summary"

    def compute_amount(self):
        """
        Rework compute amount to take into account transfers made to and from journal
        """
        session_ids = self.mapped("session_id")
        vals = {}
        transfer_from_vals = {}
        transfer_to_vals = {}
        for session_id in session_ids:
            journal_ids = self.mapped("journal_id")
            amounts = self.env["account.payment"].read_group(
                [
                    ("journal_id", "in", journal_ids.ids),
                    ("cash_control_session_id", "=", session_id.id),
                    ("payment_type", "!=", "transfer"),
                ],
                ["amount:sum"],
                ["journal_id"],
            )
            for amount in amounts:
                vals[amount["journal_id"][0]] = amount["amount"]

            transfer_from_amounts = self.env["account.payment"].read_group(
                [
                    ("journal_id", "in", journal_ids.ids),
                    ("cash_control_session_id", "=", session_id.id),
                    ("payment_type", "=", "transfer"),
                ],
                ["amount:sum"],
                ["journal_id"],
            )
            for amount in transfer_from_amounts:
                transfer_from_vals[amount["journal_id"][0]] = amount["amount"]

            transfer_to_amounts = self.env["account.payment"].read_group(
                [
                    ("journal_id", "in", journal_ids.ids),
                    ("cash_control_session_id", "=", session_id.id),
                    ("payment_type", "=", "transfer"),
                ],
                ["amount:sum"],
                ["destination_journal_id"],
            )
            for amount in transfer_to_amounts:
                transfer_to_vals[amount["destination_journal_id"][0]] = amount["amount"]

            for summary in self.filtered(
                lambda line: line.session_id.id == session_id.id
            ):
                summary.amount = (
                    vals.get(summary.journal_id.id, 0)
                    + transfer_to_vals.get(summary.journal_id.id, 0)
                    - transfer_from_vals.get(summary.journal_id.id, 0)
                )
