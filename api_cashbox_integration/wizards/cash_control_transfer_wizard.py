# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime


class CashControlTransferWizard(models.TransientModel):
    _inherit = 'cash.control.transfer.wizard'
    
    def api_transfer_cash(self, ref: str = False, session_id:models.Model = False):
        if self.operation == 'transfer_to_cash':
            vals = {
                'name': 'Destino: %s'%(self.dest_cash_control_id.name),
                'orig_journal_id': self.orig_journal_id.id,
                'dest_cash_control_id': self.dest_cash_control_id.id,
                'amount': self.amount,
            }
            transfer = self.env['cash.control.transfer.cash'].create(vals)
            transfer.action_transfer(ref=ref,session_id=session_id)
            # transfer.action_receipt(ref=ref)
            return transfer