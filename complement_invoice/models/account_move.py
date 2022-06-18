from odoo import models,fields,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    planilla = fields.Char()

    @api.onchange('planilla')
    def _onchange_session_id_debo(self):
        session_obj = self.env['cash.control.session']
        session_id = session_obj.get_session_by_id_debo(self.planilla)
        self.cash_control_session_id = session_id