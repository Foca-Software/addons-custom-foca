from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    user_id = fields.Many2one(comodel_name='res.users', string='Responsible')
    user_ids = fields.Many2many(comodel_name='res.users', string='Assignees')


    transfer_ids = fields.Many2many(string="transfers", comodel_name='account.bank.statement.line', compute="_compute_transfer_ids")

    @api.depends("statement_id")
    def _compute_transfer_ids(self):
        for session in self:
            session.transfer_ids = self.env["account.bank.statement.line"].search(
                [("statement_id", "=", session.statement_id.id)]
            )

    @api.model
    def create(self,vals):
        res = super().create(vals)
        try:
            res.user_id = self.env.user.id
        except Exception as e:
            _logger.error(e)
        return res
