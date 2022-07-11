from odoo import models,fields

class ProductProduct(models.Model):
    _inherit='product.product'

    store_dependent_field_ids = fields.One2many(comodel_name="product.store.dependent",inverse_name="product_id",string="Store Dependent Fields",)