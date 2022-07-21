from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockPump(models.Model):
    _inherit = "stock.pump"

    pump_history_ids = fields.One2many(
        comodel_name="stock.pump.history",
        inverse_name="pump_id",
        domain=[("pump_id", "=", "id")],
        string="Pump History",
    )


class StockPumpHistory(models.Model):
    _name = "stock.pump.history"
    _description = "Stock Pump History"
    _rec_name = "cash_control_session_id"

    modified_date = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        readonly=True,
    )

    cash_control_session_id = fields.Many2one(
        "cash.control.session",
        string="Cash Control Session",
        required=True,
    )

    pump_id = fields.Many2one(
        "stock.pump",
        string="Pump",
        required=True,
    )

    initial_qty = fields.Float(string="Initial Quantity")
    final_qty = fields.Float(string="Final Quantity")
    cubic_meters = fields.Float()
    amount = fields.Float()

    def name_get(self):
        res = []
        for history_rec in self:
            res.append((history_rec.id, "%s" % history_rec.stock_pump_id.display_name))
        return res
