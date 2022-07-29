from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    config_sells_fuel = fields.Boolean(
        related="config_id.is_fuel_cashbox", string="Cashbox sells Fuel"
    )
    config_is_shop = fields.Boolean(
        related="config_id.is_shop_cashbox", string="Cashbox is Shop"
    )

    pump_ids = fields.Many2many(comodel_name="stock.pump", string="Pumps")
    fuel_move_ids = fields.One2many(
        comodel_name="fuel.move.line",
        inverse_name="session_id",
        string="Fuel Movements",
    )

    fuel_stock_picking_ids = fields.One2many(
        string="Fuel Stock Pickings",
        comodel_name="stock.picking",
        inverse_name="cash_control_session_id",
        domain="[('is_fuel_picking','=',True)]",
    )

    @api.constrains("pump_ids")
    def _check_pump_ids(self):
        for session in self:
            if not session.config_sells_fuel and session.pump_ids:
                raise ValidationError(_("That cashbox cannot have pumps associated"))

    # to be executed on cashbox opening__________________________________________
    @api.depends("pump_ids")
    def create_fuel_move_lines(self):
        """
        Creates fuel_move_lines depending on the pumps declared on session opening
        """
        for session in self:
            if not session.pump_ids:
                session.fuel_move_ids = False
            fuel_move_obj = self.env["fuel.move.line"]
            line_ids = []
            for pump in session.pump_ids:
                new_line = fuel_move_obj.create(
                    {
                        "session_id": session.id,
                        "pump_id": pump.id,
                    }
                )
                line_ids.append(new_line.id)
            _logger.info(line_ids)
            session.write({"fuel_move_ids": [(6, session.id, line_ids)]})

    @api.model
    def update_fuel_move_lines(self, fuel_move_id: int, line: dict) -> bool:
        move_line = self.env["fuel.move.line"].browse(fuel_move_id)
        del line["pump_id"]
        move_written = move_line.write(line)
        if not move_written:
            _logger.error("fuel line not written")
            return False
        return True

    def _api_edit_fuel_lines(self, data: dict) -> bool:
        """
        Edits all fuel lines depending on the pump closing data handled by the controller
        """
        for line in data:
            _logger.warning(line)
            try:
                fuel_move = self.fuel_move_ids.filtered(
                    lambda p: int(p.pump_id) == int(line.get("pump_id", False))
                )
                fuel_move_id = fuel_move.id if fuel_move else False
                if not fuel_move_id:
                    _logger.error("fuel move id not found")
                    continue
                if not self.update_fuel_move_lines(fuel_move_id, line):
                    _logger.error("fuel move not updated")
                    continue
            except Exception as e:
                _logger.error(e)
                return False
        return True

    # __________________________________________________________________________________
