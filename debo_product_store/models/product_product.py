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