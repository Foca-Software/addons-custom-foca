from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    pump_ids = fields.Many2many(comodel_name="stock.pump", string="Pumps")
    fuel_move_ids = fields.One2many(
        comodel_name="fuel.move.line",
        inverse_name="session_id",
        string="Fuel Movements",
    )

    @api.depends("pump_ids")
    # @api.onchange("pump_ids")
    def create_fuel_move_lines(self):
        for session in self:
            if not session.pump_ids:
                session.fuel_move_ids = False

            fuel_move_obj = self.env["fuel.move.line"]
            # pump_lines = [pump_obj.create({
            #     "session_id" : session.id,
            #     "pump_id" : pump.id
            # }) for pump in session.pump_ids]
            line_ids = []
            for pump in session.pump_ids:
                new_line = fuel_move_obj.create({"session_id": session.id, "pump_id": pump.id})
                line_ids.append(new_line.id)
            # _logger.info(pump_lines)
            _logger.info(line_ids)
            session.write({'fuel_move_ids' : [(6,session.id,line_ids)]})
