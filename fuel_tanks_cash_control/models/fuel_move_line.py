from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class FuelMoveLine(models.Model):
    _name = "fuel.move.line"
    _description = "Fuel Move Lines"
    # _order = "tank_id desc"

    session_id = fields.Many2one(comodel_name="cash.control.session", string="Session")
    id_debo = fields.Char(related="session_id.id_debo", string="Planilla")

    pump_id = fields.Many2one(comodel_name="stock.pump", string="Pump")
    pump_id_debo = fields.Char(related="pump_id.id_debo", string="ID DEBO")
    pump_code = fields.Char(related="pump_id.code", string="Code")
    tank_id = fields.Many2one(comodel_name="stock.location", related="pump_id.tank_id")
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="tank_id.product_id",
        string="Product",
    )
    price = fields.Float(string="Price")
    initial_qty = fields.Float(string="Initial Quantity")
    final_qty = fields.Float(string="Final Quantity")
    manual_qty = fields.Float(string="Manual Quantity")
    cubic_meters = fields.Float(string="Cubic Meters")
    amount = fields.Float(string="Amount")

    def create_stock_moves(self):
        """
        Creates stock moves for the fuel moves
        """
        stock = self.env["stock.move"]
        stock_picking = self.env["stock.picking"]
        picking_type = self.env["stock.picking.type"]
        for fuel_move in self:
            if fuel_move.cubic_meters == 0:
                continue
            picking_type_id = picking_type.search(
                [
                    ("default_location_src_id", "=", fuel_move.tank_id.id),
                    # TODO: what would happen in case of an incoming move?
                    # dest_loc = self.env.ref('stock.stock_location_customers').id
                    ("code", "=", "outgoing"),
                ],
                limit=1,
            )
            stock_picking_vals = {
                "company_id": self.env.user.company_id.id,
                "origin": fuel_move.session_id.id_debo,
                "location_id": fuel_move.tank_id.id,
                "location_dest_id": picking_type_id.default_location_dest_id.id,
                "picking_type_id": picking_type_id.id,
            }
            # TODO: create module fuel_tanks_cash_control_multi_store to add this
            try:
                multi_store_fields = {
                    "store_id": fuel_move.session_id.config_id.store_id.id
                    if fuel_move.session_id.config_id.store_id
                    else False,
                }
                if multi_store_fields:
                    stock_picking_vals.update(multi_store_fields)
            except:
                pass
            # --------------------------------------------------------------------
            stock_picking_id = stock_picking.create(stock_picking_vals)
            stock_vals = {
                "name": f"{fuel_move.session_id.id_debo}/{fuel_move.pump_id.code}",
                "product_id": fuel_move.product_id.id,
                "product_uom": fuel_move.product_id.uom_id.id,
                "quantity_done": fuel_move.cubic_meters,
            }
            picking_context = {
                "default_company_id": stock_picking_id.company_id.id,
                "default_picking_id": stock_picking_id.id,
                "default_picking_type_id": stock_picking_id.picking_type_id.id,
                "default_location_id": stock_picking_id.location_id.id,
                "default_location_dest_id": stock_picking_id.location_dest_id.id,
            }
            stock_move = stock.with_context(picking_context).create(stock_vals)
            _logger.info("stock move created:")
            _logger.info(stock_picking_id.name)
            _logger.info(stock_move.name)
            #confirm move
            stock_picking_id.action_assign()
            stock_picking_id.button_validate()
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, stock_picking_id.id)]})
            wiz.process()

