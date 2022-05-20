from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _add_lines(self, data: list):
        sale_line_obj = self.env["sale.order.line"]
        for line in data:
            new_line = sale_line_obj.create(
                {
                    "order_id": self.id,
                    "product_id": line["product_id"],
                }
            )
            new_line.product_id_change()
            new_line.write(
                {
                    "product_uom_qty": line.get("product_uom_qty")
                    or new_line.product_uom_qty,
                    "price_unit": line.get("price_unit", new_line.price_unit),
                    "pump_id": line.get("pump_id"),
                    "default_price" : line.get("default_price", new_line.product_id.lst_price),
                }
            )

    @api.depends("pump_id")
    def compute_warehouse_id(self):
        for order in self:
            for line in order.order_line:
                if line.pump_id:
                    location = line.pump_id.tank_id
                    wh_id = self.env["stock.warehouse"].search(
                        [("lot_stock_id", "=", location.id)], limit=1
                    )
                    order.warehouse_id = wh_id.id
        return True
