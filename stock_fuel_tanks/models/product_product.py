from odoo import models,fields,api,_
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_fuel = fields.Boolean(string="Fuel")