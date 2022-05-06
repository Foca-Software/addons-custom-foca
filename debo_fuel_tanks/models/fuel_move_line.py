from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class FuelMoveLine(models.Model):
    _inherit = "fuel.move.line"

    id_debo = fields.Char(related="session_id.id_debo", string="Planilla")

    pump_id_debo = fields.Char(related="pump_id.id_debo", string="ID DEBO")

    session_consumption = fields.Float(
        string="Consumption", compute="_compute_session_consumption"
    )

    @api.depends("session_id")
    def _compute_session_consumption(self):
        for fuel_move in self:
            fuel_move.session_consumption = (
                fuel_move.session_id._current_session_pump_moves_total(fuel_move.pump_id.id)
                or 0.0
            )

    def _adjustment_needed(self) -> bool:
        return self.cubic_meters != self.session_consumption

    def _requires_incoming(self) -> bool:
        return self.cubic_meters < self.session_consumption

    def _requires_outgoing(self) -> bool:
        return self.cubic_meters > self.session_consumption

    def _picking_type_domain(self) -> list:
        if self._requires_incoming():
            return [
                ("default_location_dest_id", "=", self.tank_id.id),
                ("code", "=", "incoming"),
            ]
        elif self._requires_outgoing():
            return [
                ("default_location_src_id", "=", self.tank_id.id),
                ("code", "=", "outgoing"),
            ]
        raise ValidationError("This should never happen")

    def _location_vals(self,picking_type_id : object) -> dict:
        customer_loc = self.env.ref("stock.stock_location_customers").id
        if self._requires_incoming():
            return {
                #should these moves come from customer locations?
                "location_id": picking_type_id.default_location_dest_id.id
                or customer_loc,
                "location_dest_id": self.tank_id.id,
            }
        elif self._requires_outgoing():
            return {
                "location_id": self.tank_id.id,
                "location_dest_id": picking_type_id.default_location_dest_id.id
                or customer_loc,
            }
        raise ValidationError("This should never happen")

    def create_stock_moves(self):
        """
        Creates stock moves for the fuel moves
        """
        stock = self.env["stock.move"]
        stock_picking = self.env["stock.picking"]
        picking_type = self.env["stock.picking.type"]
        customer_loc = self.env.ref("stock.stock_location_customers").id
        for fuel_move in self:
            # ____Proposed changes:____
            # if fuel_move.cubic_meters == 0 or not fuel_move._adjustment_needed():
            #     continue
            # picking_type_id = picking_type.search(
            #     fuel_move._picking_type_domain(), limit=1
            # )
            # stock_picking_vals = {
            #     "company_id": self.env.user.company_id.id,
            #     "origin": fuel_move.session_id.id_debo,
            #     "picking_type_id": picking_type_id.id,
            # }
            # stock_picking_vals.update(fuel_move._location_vals(picking_type_id))
            #______________________________________________________________________
            if fuel_move.cubic_meters == 0:
                continue
            picking_type_id = picking_type.search(
                [
                    ("default_location_src_id", "=", fuel_move.tank_id.id),
                    # TODO: what would happen in case of an incoming move?
                    ("code", "=", "outgoing"),
                ],
                limit=1,
            )
            stock_picking_vals = {
                "company_id": self.env.user.company_id.id,
                "origin": fuel_move.session_id.id_debo,
                "picking_type_id": picking_type_id.id,
                "location_id": self.tank_id.id,
                "location_dest_id": picking_type_id.default_location_dest_id.id
                or customer_loc,
            }
            stock_picking_vals.update(fuel_move._location_vals(picking_type_id))
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
            # confirm move
            stock_picking_id.action_assign()
            stock_picking_id.button_validate()
            wiz = self.env["stock.immediate.transfer"].create(
                {"pick_ids": [(4, stock_picking_id.id)]}
            )
            wiz.process()
