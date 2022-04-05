from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    id_debo = fields.Char(string="Planilla")
    
    def _api_add_user(self, user_id):
        try:
            self.user_ids = [(4,0, user_id)]
            return True
        except Exception as e:
            _logger.error(e)
            return False


    def _api_open_cashbox_pos(self, number : int = 1, coin_value : float = 0.0): #, number : int = 0, coin_value : int = 0
        self.ensure_one()
        subtotal = coin_value * number
        # action = self.statement_id.open_cashbox_id()
        # action = action['context']
        # _logger.error(action['context'])
        ctx = {}
        ctx.update(self.env.context)
        ctx['statement_id'] = self.statement_id.id #action['statement_id']
        ctx['pos_session_id'] = self.id
        ctx['default_pos_id'] = self.config_id.id
        _logger.error(ctx)
        open_dict = {
            'cashbox_lines_ids' : [(0, 0, {'number': number, 'coin_value': coin_value, 'subtotal': subtotal})],
        }
        _logger.warning(open_dict)
        wiz = self.env['account.bank.statement.cashbox'].with_context(ctx).create(open_dict)
        wiz._validate_cashbox()
        # _logger.warning(wiz)
        return wiz


    def api_action_session_close(self):
        _logger.info('clossing session....')

        if abs(self.statement_difference) > self.config_id.amount_authorized_diff:
            # Only pos manager can close statements with statement_difference greater than amount_authorized_diff.
            # if not self.user_has_groups("point_of_sale.group_pos_manager"):
            #     raise UserError(_(
            #         "Your ending balance is too different from the theoretical cash closing (%.2f), "
            #         "the maximum allowed is: %.2f. You can contact your manager to force it."
            #     ) % (self.statement_difference, self.config_id.amount_authorized_diff))
            # else:
            #     return self._warning_balance_closing()
            raise UserError(_(
                "Your ending balance is too different from the theoretical cash closing (%.2f), "
                "the maximum allowed is: %.2f. You can contact your manager to force it."
            ) % (self.statement_difference, self.config_id.amount_authorized_diff))
        # odoo 12 - session - action_pos_session_close
        # Close CashBox
        self._check_pos_session_balance()
        company_id = self.config_id.company_id.id
        ctx = dict(self.env.context, force_company=company_id,
                   company_id=company_id)
        ctx_notrack = dict(ctx, mail_notrack=True)
        for st in self.statement_ids:
            # TODO: CERRAR SOLO LOS STATEMENTS DE CASH, EL DE TARJETA ES COMPARTIDO ENTRE TODAS LAS SUCURSALES - 15 TARJETAS APROX.
            # VER COMO RESOLVER EL STATEMENT DE TARJETA QUE ES COMPARTIDO.
            if (st.journal_id.type not in ['bank', 'cash']):
                raise UserError(
                    _("The journal type for your payment method should be bank or cash."))
            st.with_context(ctx_notrack).sudo().button_confirm_bank()
        return self._validate_session()
#trash
        # default_vals = self.env['account.bank.statement.cashbox'].default_get(action['context'])
        # _logger.warning(default_vals)

        #action = self.cash_register_id.open_cashbox_id()
        # action['view_id'] = self.env.ref(
        #     'account.view_account_bnk_stmt_cashbox_footer').id
        # open_dict.update(default_vals)
        # wiz = self.statement_id.with_context(default_vals).create(open_dict)