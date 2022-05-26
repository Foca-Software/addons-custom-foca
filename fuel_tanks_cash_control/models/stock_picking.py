from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _default_cash_control_session_id(self):
        session = self.env['cash.control.session'].search([
            ('user_ids', 'in', self.env.uid),
            ('state', '=', 'opened')
        ])
        if not session:
            return False
            # raise ValidationError(_("There is not open cash session for de the current user. Please open a cash session"))
        return session.id

    cash_control_session_id = fields.Many2one(
        comodel_name="cash.control.session",
        string="Cash Control Session",
        default= _default_cash_control_session_id,
        # related="sale_id.cash_control_session_id",
        store=True
    )
