from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("product_id", "location_dest_id", "qty_done")
    def check_tank_capacity(self):
        for move in self:
            if not move.product_id.is_fuel or \
                move.location_dest_id.usage == 'customer':
                continue
            stock_quant_obj = self.env["stock.quant"]
            domain = [
                ("product_id", "=", move.product_id),
                ("location_id", "=", move.location_dest_id),
            ]
            product_qty = stock_quant_obj.search(domain).quantity

            if move.qty_done + product_qty > move.location_dest_id.capacity:
                raise ValidationError("You cannot exceed tank capacity")

    @api.constrains("product_id","location_dest_id")
    def check_tank_content(self):
        for move in self:
            if not move.product_id.is_fuel or \
                move.location_dest_id.usage == 'customer':
                continue
            if move.product_id != location_dest_id.product_id:
                raise ValidationError("You cannot mix products in tanks")
            
