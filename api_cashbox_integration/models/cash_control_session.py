from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    has_final_cash_transfer = fields.Boolean()

    is_confirmed_in_debo_pos = fields.Boolean()
    
    change_received = fields.Float(digits=(16,2),help="Amount of money received from previous session")

    change_delivered = fields.Float(digits=(16,2),help="Amount of money left for next session")

    def confirm_session(self, change_delivered:float = False):
        for session in self:
            if not session.change_delivered:
                session.change_delivered = change_delivered
            session.is_confirmed_in_debo_pos = True

    show_confirmation_alert = fields.Boolean(compute="_compute_show_confirmation_alert")

    def _compute_show_confirmation_alert(self):
        for session in self:
            condition = session.state in self._alert_states() and not session.is_confirmed_in_debo_pos
            session.show_confirmation_alert = condition

    def _alert_states(self):
        return ['closed']

    def _api_add_user(self, user_id):
        try:
            self.write({"user_ids" : [(4, user_id)]})
            return True
        except Exception as e:
            _logger.error(e)
            return False

    def _api_remove_user(self,user_id):
        try:
            self.write({"user_ids" : [(3, user_id)]})
            return True
        except Exception as e:
            _logger.error(e)
            return False


    def _api_open_cashbox_pos(self, number : int = 1, coin_value : float = 0.0): #, number : int = 0, coin_value : int = 0
        self.ensure_one()
        subtotal = coin_value * number
        ctx = {}
        ctx.update(self.env.context)
        ctx['statement_id'] = self.statement_id.id
        ctx['pos_session_id'] = self.id
        ctx['default_pos_id'] = self.config_id.id
        open_dict = {
            'cashbox_lines_ids' : [(0, 0, {'number': number, 'coin_value': coin_value, 'subtotal': subtotal})],
        }
        wiz = self.env['account.bank.statement.cashbox'].with_context(ctx).create(open_dict)
        wiz._validate_cashbox()
        return wiz


    def api_action_session_close(self):
        self.state = "closed"
        # self.statement_id.state = "waiting_confirmation"