from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    transfer_ids = fields.Many2many(string="transfers", comodel_name='account.bank.statement.line', compute="_compute_transfer_ids")

    @api.depends("statement_id")
    def _compute_transfer_ids(self):
        for session in self:
            session.transfer_ids = self.env["account.bank.statement.line"].search(
                [("statement_id", "=", session.statement_id.id)]
            )
