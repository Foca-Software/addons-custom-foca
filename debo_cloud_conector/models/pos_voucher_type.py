from odoo import fields, models, api, _

class PosVoucherType(models.Model):
    _name = 'pos.voucher.type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')