from odoo import models,fields,api,_
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_fuel = fields.Boolean(string="Fuel")
    # , related="product_tmpl_id.is_fuel"

    # @api.onchange('is_fuel')
    # def update_is_fuel_template_id(self):
    #     self.product_tmpl_id.write({'is_fuel':self.is_fuel})