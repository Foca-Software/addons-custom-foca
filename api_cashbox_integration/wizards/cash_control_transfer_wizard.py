# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime


class CashControlTransferWizard(models.TransientModel):
    _inherit = 'cash.control.transfer.wizard'
    
    def api_transfer_cash(self, ref: str = False):
        if self.operation == 'transfer_to_cash':
            vals = {
                'name': 'Destino: %s'%(self.dest_cash_control_id.name),
                'orig_journal_id': self.orig_journal_id.id,
                'dest_cash_control_id': self.dest_cash_control_id.id,
                'amount': self.amount,
            }
            transfer = self.env['cash.control.transfer.cash'].create(vals)
            transfer.action_transfer(ref=ref)
            # transfer.action_receipt(ref=ref)
        elif self.operation == 'transfer_to_bank':
            payment_type = 'outbound'
            payment_methods = self.bank_journal_id.outbound_payment_method_ids
            payment_method = payment_methods.filtered(
                    lambda x: x.code == 'manual')
            if not payment_method:
                raise ValidationError(_(
                    'Pay now journal must have manual method!'))
            vals = {
                'journal_id': self.orig_journal_id.id,
                'destination_journal_id': self.bank_journal_id.id,
                'amount': self.amount,
                'payment_date': datetime.today().strftime('%Y-%m-%d'),
                'payment_type': 'transfer',
                'payment_method_id': payment_method.id,
            }
            transfer = self.env['account.payment'].create(vals)
            transfer.post()