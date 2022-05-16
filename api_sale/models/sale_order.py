from odoo import models,fields,api,_ 

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit="sale.order"

    def _add_lines(self, data: list):
        sale_line_obj = self.env['sale.order.line']
        for line in data:
            new_line = sale_line_obj.create(
                {
                    "order_id": self.id,
                    "product_id": line["product_id"],
                }
            )
            new_line.product_id_change()
            new_line.write({
                "product_uom_qty": line.get("product_uom_qty") or new_line.product_uom_qty,
                "price_unit": line.get("price_unit") or new_line.price_unit,
                "pump_id" : line.get("pump_id"),
            })