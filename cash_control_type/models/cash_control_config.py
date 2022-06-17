from odoo import models,fields,api

class CashControlConfig(models.Model):
    _inherit = 'cash.control.config'

    type_id = fields.Many2one(comodel_name='cash.control.config.type', string='Cashbox Type')

    is_fuel_cashbox = fields.Boolean(related="type_id.sells_fuel")

    is_shop_cashbox = fields.Boolean(_compute="_compute_is_shop_cashbox")

    def _compute_is_shop_cashbox(self):
        for config in self:
            config.is_shop_cashbox = config.type_id.place_of_sale in ['shop','box']