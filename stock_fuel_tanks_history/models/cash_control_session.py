# pylint: disable=access-member-before-definition, attribute-defined-outside-init
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    @api.model
    def update_fuel_move_lines(self, fuel_move_id: int, line: dict) -> bool:
        """Create the history record for the fuel move line

        Args:
            fuel_move_id (int): Fuel move line id
            line (dict): Fuel move line data

        Returns:
            bool: True if the fuel move line was updated
        """
        self.ensure_one()
        res = super().update_fuel_move_lines(fuel_move_id, line)
        if res:
            ctx = dict(self.env.context)
            ctx["lang"] = self.create_uid.lang
            self.env.context = ctx
            session = self
            move_line = self.env["fuel.move.line"].browse(fuel_move_id)
            pump = move_line.pump_id
            hist_vals = {
                "modified_date": fields.Datetime.now(),
                "cash_control_session_id": session.id,
                "pump_id": pump.id,
                "initial_qty": line.get("initial_qty"),
                "final_qty": line.get("final_qty"),
                "cubic_meters": line.get("cubic_meters"),
                "price": line.get("price"),
                "amount": line.get("amount"),
                "details": _("Created from session closing."),
            }
            _logger.info("Creating pump history for pump %s", pump.display_name)
            pump.pump_history_ids = [(0, 0, hist_vals)]
        return True
