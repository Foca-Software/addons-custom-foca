from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ComplementInvoiceConfig(models.Model):
    _name = "complement.invoice.config"
    _description = "complement.invoice.config"

    name = fields.Char(compute="_compute_name")

    turn_id = fields.Many2one(comodel_name="cash.control.turn", string="Turn")
    day = fields.Selection(
        selection=[
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
        ],
    )
    config_line_ids = fields.One2many(
        comodel_name="complement.invoice.config.line",
        inverse_name="config_id",
        string="Partner Invoices",
    )

    cash_control_config_id = fields.Many2one(
        comodel_name="cash.control.config",
        domain=[("type_id.uses_complement_invoice", "=", True)],
    )

    total_percentage = fields.Float(compute="_compute_total_percentage")

    def _compute_name(self):
        for config in self:
            if config.cash_control_config_id.name and config.turn_id.name:
                config.name = (
                    f"{config.cash_control_config_id.name} - {config.turn_id.name}"
                )
            else:
                config.name = _("New Configuration")

    def _compute_total_percentage(self):
        for config in self:
            if config.config_line_ids:
                config.total_percentage = sum(
                    [
                        config.mapped("config_line_ids")
                        .filtered(lambda x: x)
                        .mapped("percentage")
                    ][0]
                )
            else:
                config.total_percentage = False

    @api.constrains("turn_id", "day", "cash_control_config_id")
    def _constraint_turn_day(self):
        all_configs = self.env["complement.invoice.config"].search([])
        for config in all_configs - self:
            if (
                config.turn_id.id == self.turn_id.id
                and config.day == self.day
                and config.cash_control_config_id.id == self.cash_control_config_id.id
            ):
                raise ValidationError(
                    "Only one config can exist for that day + turn + cashbox combination"
                )
