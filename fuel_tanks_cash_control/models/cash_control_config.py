from odoo import models, fields

class CashControlConfig(models.Model):
    _inherit = "cash.control.config"

    is_fuel_cashbox = fields.Boolean()
    is_shop_cashbox = fields.Boolean()

