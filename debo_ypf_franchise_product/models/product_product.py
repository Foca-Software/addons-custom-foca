from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_ypf_franchise_product = fields.Boolean(
        related="product_tmpl_id.is_ypf_franchise_product"
    )

    ypf_description = fields.Text(readonly=True)
    ypf_internal_code = fields.Char(readonly=True)
    ypf_barcode = fields.Char(readonly=True)

    ypf_categ_id = fields.Many2one(comodel_name="product.category", string="Category",readonly=True)
    ypf_cost = fields.Float(readonly=True)

    #'rubro'
    ypf_product_category_id = fields.Many2one(
        comodel_name="ypf.product.category", readonly=True
    )

    #'rubro mayor'
    # parent would be better but they are not actually parent-child related so...major
    ypf_major_product_category_id = fields.Many2one(
        comodel_name="ypf.major.product.category",
        readonly=True,
    )

    ypf_product_uom_id = fields.Many2one(comodel_name="uom.uom", readonly=True)

    ypf_product_uom_po_id = fields.Many2one(comodel_name="uom.uom", readonly=True, string="Purchase UOM")

    ypf_pricelist = fields.Many2one(
        comodel_name="product.pricelist",
        domain=[("is_ypf_pricelist", "=", True)],
        readonly=True,
    )

    ypf_price = fields.Float(string="YPF Price",readonly=True) #compute?

    ypf_tax_ids = fields.Many2many(
        comodel_name="account.tax", domain=[("is_ypf_tax", "=", True)], readonly=True
    )

    store_ids = fields.Many2many(comodel_name="res.store", readonly=True)  # compute?
