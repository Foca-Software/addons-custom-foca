from odoo import models,fields

class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_ypf_tax = fields.Boolean(string="Is YPF Tax",readonly=True)