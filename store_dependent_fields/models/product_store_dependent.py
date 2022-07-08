from calendar import c
from odoo import models, fields, api, _


class ProductStoreDependent(models.Model):
    _name = "product.store.dependent"
    _description = "Product Store Dependent"

    product_id = fields.Many2one(comodel_name="product.product")

    store_id = fields.Many2one(comodel_name="res.store", string="Store", required=True)

    name = fields.Char()

    def _default_currency_id(self):
        return self.env.ref("base.ARS")

    currency_id = fields.Many2one(
        comodel_name="res.currency", default=_default_currency_id
    )
    price = fields.Monetary()
    pricelist_id = fields.Many2one(comodel_name="product.pricelist")
