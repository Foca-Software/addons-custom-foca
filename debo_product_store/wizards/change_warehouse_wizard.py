from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ChangeWarehouseWizard(models.TransientModel):
    _name = "change.warehouse.wizard"
    _description = "Change Warehouse Wizard"

    product_ids = fields.Many2many(
        comodel_name="product.product",
        default=lambda self: self.env.context.get("active_ids"),
    )

    def _default_warehouse_ids(self):
        product_ids = self.env.context.get("active_ids")

        return (
            self.env["product.product"]
            .browse(product_ids)
            .warehouse_ids.ids
        )

    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse", default=_default_warehouse_ids, string="Warehouses"
    )

    def action_confirm(self):
        for product in self.product_ids:
            product.warehouse_ids = self.warehouse_ids
            for line in product.store_dependent_field_ids:
                sector_ids = product.warehouse_ids.filtered(
                    lambda wh: wh.store_id.id == line.store_id.id
                ).mapped("sector_id")
                line.sector_ids = sector_ids
