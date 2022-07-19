from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class EnableDisableProduct(models.TransientModel):
    _name = "enable.disable.product"
    _description = "Enable Disable Product"

    product_ids = fields.Many2many(
        comodel_name="product.product",
        default=lambda self: self.env.context.get("active_ids"),
    )

    store_id = fields.Many2one(comodel_name="res.store")

    sector_ids = fields.Many2many(comodel_name="sector.sector")

    def action_apply(self):
        _logger.info("acatalboton")
        for product in self.product_ids:
            store_line = self._get_product_store_line(product, self.store_id)
            if not store_line:
                line = product.store_dependent_field_ids.create(
                    {
                        "product_id": product.id,
                        "sector_ids": self.sector_ids.ids,
                        "store_id": self.store_id.id,
                        "enable": True,
                    }
                )
                line._onchange_product_id()
            else:
                store_line.write(
                    {
                        "store_id": self.store_id.id,
                        "sector_ids": self.sector_ids.ids,
                        "enable": True,
                    }
                )

    def _get_product_store_line(self, product, store_id):
        line_id = product.store_dependent_field_ids.filtered(
            lambda line: line.store_id.id == store_id.id
        )
        store_is_configured = line_id != False
        return line_id if store_is_configured else False

    # TODO:
    # Diferentes configuraciones para == store != sector
