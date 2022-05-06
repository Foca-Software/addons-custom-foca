from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    # TODO: group pending stock moves by pump_id
    def _current_session_pump_moves_total(self, pump_id: int) -> float:
        """
        Returns the total amount of fuel moves for the current session and pump
        """
        return self.env["stock.move"].read_group(
            domain=[
                ("picking_id", "in", self.fuel_stock_picking_ids.ids),
                ("picking_id.pump_id", "=", pump_id),
            ],
            fields=["product_uom_qty"],
            groupby=["product_id"],
        )[0]["product_uom_qty"]

    def action_test_button(self):
        _logger.warning(self._current_session_pump_moves_total(8))

    def create_stock_moves(self):
        """
        Creates stock moves for the fuel moves
        """
        for session in self:
            session.fuel_move_ids.create_stock_moves()
