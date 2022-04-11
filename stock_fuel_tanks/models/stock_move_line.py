from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning

import logging

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    pump_id = fields.Many2one(comodel_name="stock.pump", string="pump")

    @api.constrains("product_id", "location_dest_id", "qty_done")
    def check_tank_capacity(self):
        for move in self:
            if not move.product_id.is_fuel or move.location_dest_id.usage == "customer":
                continue
            stock_quant_obj = self.env["stock.quant"]
            domain = [
                ("product_id", "=", move.product_id.id),
                ("location_id", "=", move.location_dest_id.id),
            ]
            product_qty = stock_quant_obj.search(domain).quantity
            _logger.warning(move.qty_done)
            _logger.warning(product_qty)
            _logger.warning(move.location_dest_id.capacity)
            # if move.product_uom_qty + product_qty > move.location_dest_id.capacity:
            #     raise Warning("Confirming this transfer will exceed tank capacity")
            if move.qty_done + product_qty > move.location_dest_id.capacity:
                raise ValidationError("You cannot exceed tank capacity")

    @api.constrains("product_id", "location_dest_id")
    def check_tank_content(self):
        for move in self:
            if not move.product_id.is_fuel or move.location_dest_id.usage == "customer":
                continue
            if move.product_id != move.location_dest_id.product_id:
                raise ValidationError("You cannot mix products in tanks")
