from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ComplementInvoiceConfig(models.Model):
    _name = "complement.invoice.config"
    _description = "complement Invoice Configuration"

    name = fields.Char(compute="_compute_name")

    # turn_id = fields.Many2one(comodel_name="cash.control.turn", string="Turn")
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
    summary_ids = fields.One2many(comodel_name="complement.invoice.config.summary",
    inverse_name="config_id",
    string="Summary")

    

    @api.model
    def create(self,vals):
        config_type_product_ids = self.env['cash.control.config.type'].search([('config_ids','in',[vals['cash_control_config_id']])]).ci_product_ids
        vals['summary_ids'] = [(0,0,{'product_id':product.id}) for product in config_type_product_ids]
        res = super().create(vals)
        return res
        

    def _compute_name(self):
        day_values = {
            "1":_("Monday"),
            "2":_("Tuesday"),
            "3":_("Wednesday"),
            "4":_("Thursday"),
            "5":_("Friday"),
            "6":_("Saturday"),
            "7":_("Sunday"),
        }
        for config in self:
            if config.cash_control_config_id.name and config.day:
                config.name = (
                    f"{config.cash_control_config_id.name} - {day_values[config.day]}"
                )
            else:
                config.name = _("New Configuration")


    @api.constrains("day", "cash_control_config_id")
    def _constraint_turn_day(self):
        all_configs = self.env["complement.invoice.config"].search([])
        for config in all_configs - self:
            if (
                # config.turn_id.id == self.turn_id.id
                config.day == self.day
                and config.cash_control_config_id.id == self.cash_control_config_id.id
            ):
                raise ValidationError(
                    "Only one config can exist for that day + turn + cashbox combination"
                )
