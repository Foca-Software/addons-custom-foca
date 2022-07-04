from odoo import models,fields

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_ypf_pricelist = fields.Boolean(string="Is YPF Pricelist",readonly=True)