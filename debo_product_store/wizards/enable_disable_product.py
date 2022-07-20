from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)


class EnableDisableProduct(models.TransientModel):
    _name = "enable.disable.product"
    _description = "Enable Disable Product"

    product_ids = fields.Many2many(
        comodel_name="product.product",
        default=lambda self: self.env.context.get("active_ids"),
    )

    store_ids = fields.Many2many(comodel_name="res.store")

    sector_ids_domain = fields.Char(compute="_compute_sector_ids_domain")

    @api.depends("product_ids")
    def _compute_sector_ids_domain(self):
        for wizard in self:
            available_sector_ids = wizard.product_ids.warehouse_ids.mapped("sector_id")
            wizard.sector_ids_domain = json.dumps(
                [("id", "in", available_sector_ids.ids)]
            )

    sector_ids = fields.Many2many(comodel_name="sector.sector")

    enable_all = fields.Boolean(
        help="Activating this will make all selected products available for selected stores"
    )

    def enable_all_products(self):
        product_ids = self.env.context.get("active_ids")
        _logger.info(product_ids)
        for product in product_ids:
            for line in product.store_dependent_field_ids:
                line.enabled = True

    def action_apply(self):
        """Add or edits store dependent fields for all products selectedfor all stores selected.
        Each store line should have only sectors available for store warehouses that have that sector

        Returns:
            models.Model: store_dependend_field_ids in case we need the new values
        """
        for product in self.product_ids:
            for store in self.store_ids:
                store_line = self._get_product_store_line(product, store)
                sector_ids = self.filter_sector_by_store(product, store)
                if not store_line:
                    # store_line should only be False if a new store is created
                    #since line addition occurs on product.product creation
                    line = product.store_dependent_field_ids.create(
                        {
                            "product_id": product.id,
                            "sector_ids": sector_ids.ids,
                            "store_id": store.id,
                            "enabled": self.enable_all,
                        }
                    )
                    line._onchange_product_id()
                else:
                    store_line.write(
                        {
                            "store_id": store.id,
                            "sector_ids": sector_ids.ids,
                            "enabled": self.enable_all,
                        }
                    )
        return self.product_ids.store_dependent_field_ids

    def filter_sector_by_store(
        self, product: models.Model, store: models.Model
    ) -> models.Model:
        """get sectors available for warehouses of line store

        Args:
            product (models.Model): product.product
            store (models.Model): res.store

        Returns:
            models.Model: sector.sector
        """
        product_store_warehouses = product.warehouse_ids.filtered(
            lambda wh: wh.store_id.id == store.id
        )
        store_sectors = product_store_warehouses.mapped("sector_id")
        sector_ids = self.sector_ids.filtered(lambda sector: sector.id in store_sectors)
        return sector_ids

    def _get_product_store_line(self, product, store_id):
        line_id = product.store_dependent_field_ids.filtered(
            lambda line: line.store_id.id == store_id.id
        )
        store_is_configured = line_id != False
        return line_id if store_is_configured else False
