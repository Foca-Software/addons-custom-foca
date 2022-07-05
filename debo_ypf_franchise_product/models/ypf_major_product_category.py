from odoo import models, fields, api


class YPFMajorProductCategory(models.Model):
    _name = "ypf.major.product.category"
    _description = "YPF Major Product Category"

    name = fields.Char(readonly=True)
    code = fields.Char(readonly=True)

    product_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="ypf_major_product_category_id",
        readonly=True,
    )
