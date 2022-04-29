from odoo import models,fields,api,_
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_fuel = fields.Boolean(string="Fuel", related="product_variant_id.is_fuel")

