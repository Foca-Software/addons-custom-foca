from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    pump_test_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="cc_session_pump_test_rel",
        string="Pump test lines",
        compute="_compute_pump_test_line_ids",
    )

    def _compute_pump_test_line_ids(self):
        for session in self:
            pump_test_line_ids = (
                self.env["sale.order.line"]
                .search(
                    [
                        ("order_id.debo_transaction_type", "=", "pump_test"),
                        ("order_id.cash_control_session_id", "=", session.id),
                    ]
                )
                .ids
            )
            session.pump_test_line_ids = pump_test_line_ids

    other_dispatch_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="cc_session_other_dispatch_rel",
        string="Other Dispatch lines",
        compute="_compute_other_dispatch_line_ids",
    )

    def _compute_other_dispatch_line_ids(self):
        for session in self:
            other_dispatch_line_ids = (
                self.env["sale.order.line"]
                .search(
                    [
                        ("order_id.debo_transaction_type", "=", "other_dispatch"),
                        ("order_id.cash_control_session_id", "=", session.id),
                    ]
                )
                .ids
            )
            session.other_dispatch_line_ids = other_dispatch_line_ids


    def _compute_invoice_ids(self):
        for session in self:
            internal_journal_ids = [
                self.env.ref("api_sale.pump_test").id,
                self.env.ref("api_sale.other_dispatch").id,
            ]
            session.invoice_ids = self.env["account.move"].search(
                [
                    ("cash_control_session_id", "=", session.id),
                    ("journal_id.type", "in", ["sale", "purchase"]),
                    ("journal_id", "not in", internal_journal_ids),
                ]
            )

    # TODO: group pending stock moves by pump_id
    def _current_session_pump_moves_total(self, pump_id: int) -> float:
        """
        Returns the total amount of fuel moves for the current session and pump
        """
        move = self.env["stock.move"].read_group(
            domain=[
                ("picking_id", "in", self.fuel_stock_picking_ids.ids),
                ("picking_id.pump_id", "=", pump_id),
            ],
            fields=["product_uom_qty"],
            groupby=["product_id"],
        )
        return move[0]["product_uom_qty"]

    def action_test_button(self):
        _logger.warning(self._current_session_pump_moves_total(8))

    def create_stock_moves(self):
        """
        Creates stock moves for the fuel moves
        """
        for session in self:
            session.fuel_move_ids.create_stock_moves()
