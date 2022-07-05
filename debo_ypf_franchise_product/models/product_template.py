from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_ypf_franchise_product = fields.Boolean(readonly=False)
