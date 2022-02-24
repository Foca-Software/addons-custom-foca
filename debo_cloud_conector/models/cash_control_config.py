from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class CashControlConfig(models.Model):
    _inherit = "cash.control.config"

    # @api.model
    def api_open_cashbox(self, number : int = 1, coin_value : float = 0.0):
        if not self.session_state:
            self.open_session()
        self.check_user()
        return self.current_session_id.with_context(balance='start')._api_open_cashbox_pos(coin_value=coin_value, number=number)

class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    def _api_open_cashbox_pos(self, number : int = 1, coin_value : float = 0.0): #, number : int = 0, coin_value : int = 0
        self.ensure_one()
        subtotal = coin_value * number
        action = self.statement_id.open_cashbox_id()
        action = action['context']
        # _logger.error(action['context'])
        ctx = {}
        ctx.update(self.env.context)
        ctx['statement_id'] = action['statement_id']
        ctx['pos_session_id'] = self.id
        ctx['default_pos_id'] = self.config_id.id
        # _logger.error(ctx)
        open_dict = {
            'cashbox_lines_ids' : [(0, 0, {'number': number, 'coin_value': coin_value, 'subtotal': subtotal})],
        }
        _logger.warning(open_dict)
        wiz = self.env['account.bank.statement.cashbox'].with_context(ctx).create(open_dict)
        wiz._validate_cashbox()
        # _logger.warning(wiz)
        return wiz

#trash
        # default_vals = self.env['account.bank.statement.cashbox'].default_get(action['context'])
        # _logger.warning(default_vals)

        #action = self.cash_register_id.open_cashbox_id()
        # action['view_id'] = self.env.ref(
        #     'account.view_account_bnk_stmt_cashbox_footer').id
        # open_dict.update(default_vals)
        # wiz = self.statement_id.with_context(default_vals).create(open_dict)