import logging
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    store_dependent_field_ids = fields.One2many(
        comodel_name="product.store.dependent",
        inverse_name="product_id",
        string="Store Dependent Fields",
        ondelete="restrict",
    )

    def enable_all_products(self):
        # product_ids = self.env.context.get('active_ids')
        logging.info(self)
        for product in self:
            for line in product.store_dependent_field_ids:
                line.enabled = True

    @api.model
    def create(self, vals):
        store_ids = self.env["res.store"].search([])
        vals["store_dependent_field_ids"] = [
            (0, 0, {"store_id": store.id, "product_id": self.id}) for store in store_ids
        ]
        res = super().create(vals)
        for line in res.store_dependent_field_ids:
            line._onchange_product_id()
        return res

    def _get_debo_fields(self):
        debo_fields = super()._get_debo_fields()
        store_fields = []
        for store_line in self.store_dependent_field_ids:
            fields = {
                "store_id": store_line.store_id.id,
                "price": store_line.price,
                "pricelist": store_line.pricelist_id.id,
                "internal_reference": store_line.internal_reference,
                "barcode": store_line.barcode,
                "category": store_line.categ_id.id,
                "taxes": store_line.taxes_id.ids,
                "cost": store_line.cost,
                "sectors": store_line.sector_ids.mapped("code"),
                "enabled": store_line.enabled,
            }
            store_fields.append(fields)
        logging.info(store_fields)
        debo_fields["store_dependent_fields"] = store_fields
        return debo_fields
