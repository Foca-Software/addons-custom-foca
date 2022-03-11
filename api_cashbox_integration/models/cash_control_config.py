from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class CashControlConfig(models.Model):
    _inherit = "cash.control.config"

    id_debo = fields.Char(related="current_session_id.id_debo", string="Planilla actual")
    # @api.model
    def api_open_cashbox(self, balance, number : int = 1, coin_value : float = 0.0):
        if not self.session_state:
            self.open_session()
        self.check_user()
        return self.current_session_id.with_context(balance=balance)._api_open_cashbox_pos(coin_value=coin_value, number=number)

    def api_close_session(self):
        self.check_user()
        self.current_session_id.action_session_close()
        self.current_session_id = False
        self.transfer_pendientes = False
        return True
