from odoo import models, fields, api


class YPFProductCategory(models.Model):
    _name = "ypf.product.category"
    _description = "YPF Product Category"

    name = fields.Char(readonly=True)
    code = fields.Char(readonly=True)

    product_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="ypf_product_category_id",
        readonly=True,
    )
