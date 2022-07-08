from calendar import c
from odoo import models, fields, api, _


class ProductStoreDependent(models.Model):
    _name = "product.store.dependent"
    _description = "Product Store Dependent"

    product_id = fields.Many2one(comodel_name="product.product")

    store_id = fields.Many2one(comodel_name="res.store", string="Store", required=True)

    name = fields.Char(defaut=lambda self: self.product_id.name)

    def _default_currency_id(self):
        return self.env.ref("base.ARS")

    currency_id = fields.Many2one(
        comodel_name="res.currency", default=_default_currency_id
    )
    price = fields.Monetary(defaut=lambda self: self.product_id.lst_price)
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        defaut=lambda self: self.product_id.pricelist_id,
    )

    internal_reference = fields.Char()
    barcode = fields.Char(defaut=lambda self: self.product_id.barcode)
    categ_id = fields.Many2one(
        comodel_name="product.category", defaut=lambda self: self.product_id.categ_id
    )
    tax_ids = fields.Many2many(
        comodel_name="account.tax", defaut=lambda self: self.product_id.tax_ids
    )
    cost = fields.Monetary()
    uom_id = fields.Many2one(
        comodel_name="uom.uom", defaut=lambda self: self.product_id.uom_id
    )
    uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase UOM",
        defaut=lambda self: self.product_id.uom_po_id,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.price = self.product_id.lst_price
        self.pricelist_id = self.product_id.pricelist_id