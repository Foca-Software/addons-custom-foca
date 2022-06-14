from odoo import models, fields, api, _


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
