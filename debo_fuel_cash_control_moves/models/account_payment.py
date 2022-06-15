from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    debo_transaction_type = fields.Selection(
        selection=[("card_batch", "Card Batch"), ("register_check", "Register Check")]
    )
