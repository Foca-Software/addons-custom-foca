from odoo import models, fields, api, _

class CashControlConfig(models.Model):
    _inherit = 'cash.control.config'

    store_id = fields.Many2one(
        'res.store',
        string="Store"
    )