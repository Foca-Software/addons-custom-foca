from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductStoreDependent(models.Model):
    _name = "product.store.dependent"
    _description = "Product Store Dependent"

    product_id = fields.Many2one(
        comodel_name="product.product",
    )

    store_id = fields.Many2one(comodel_name="res.store", string="Store", required=True)

    name = fields.Char()

    def _default_currency_id(self):
        return self.env.ref("base.ARS")

    currency_id = fields.Many2one(
        comodel_name="res.currency", default=_default_currency_id
    )
    price = fields.Monetary()
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
    )

    internal_reference = fields.Char()
    barcode = fields.Char()
    categ_id = fields.Many2one(
        comodel_name="product.category",
    )
    taxes_id = fields.Many2many(
        comodel_name="account.tax",
    )
    cost = fields.Monetary()
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
    )
    uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase UOM",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.price = self.product_id.lst_price
        self.pricelist_id = self.product_id.pricelist_id
        self.barcode = self.product_id.barcode
        self.categ_id = self.product_id.categ_id
        self.taxes_id = self.product_id.taxes_id
        self.uom_id = self.product_id.uom_id
        self.uom_po_id = self.product_id.uom_po_id

    @api.constrains("store_id")
    def _constraint_store_id(self):
        for line in self:
            domain = [
                ("store_id", "=", line.store_id.id),
                ("product_id", "=", line.product_id.id),
            ]
            if self.search_count(domain) > 1:
                raise ValidationError(
                    _("You cannot have multiple settings for the same Store")
                )
