from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import json

_logger = logging.getLogger(__name__)


class ComplementInvoiceConfig(models.Model):
    _name = "complement.invoice.config"
    _description = "complement Invoice Configuration"

    company_id = fields.Many2one(
        comodel_name="res.company", compute="_compute_company_id"
    )

    user_id = fields.Many2one(
        comodel_name="res.users", default=lambda self: self.env.user.id
    )

    user_store_ids = fields.Many2many(related="user_id.store_ids")
    store_ids_count = fields.Integer(compute="_compute_store_ids_count")

    @api.depends('user_store_ids')
    def _compute_store_ids_count(self):
        for config in self:
            config.store_ids_count = len(config.user_store_ids.ids)

    def _default_store_id(self):
        return self.env.user.store_id

    store_id = fields.Many2one(comodel_name="res.store", default=_default_store_id)

    store_id_domain = fields.Char(
        compute="_compute_store_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("user_store_ids")
    def _compute_store_id_domain(self):
        for rec in self:
            rec.store_id_domain = json.dumps([("id", "in", rec.user_store_ids.ids)])

    cash_id_domain = fields.Char(
        compute="_compute_cash_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("user_store_ids")
    def _compute_cash_id_domain(self):
        for rec in self:
            rec.cash_id_domain = json.dumps(
                [
                    ("store_id", "in", rec.user_store_ids.ids),
                    ("type_id.uses_complement_invoice", "=", True),
                ]
            )

    perceptions_apply = fields.Boolean()

    name = fields.Char(compute="_compute_name")
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
        string="Configuration Lines",
    )

    cash_control_config_id = fields.Many2one(
        comodel_name="cash.control.config",
    )
    summary_ids = fields.One2many(
        comodel_name="complement.invoice.config.summary",
        inverse_name="config_id",
        string="Summary",
    )

    total_percentage = fields.Float(compute="_compute_total_percentage")

    def _compute_company_id(self):
        for config in self:
            config.company_id = (
                config.cash_control_config_id.company_id or self.env.company
            )

    def _compute_total_percentage(self):
        for config in self:
            if config.config_line_ids:
                total = sum(config.config_line_ids.mapped("percentage"))
                lines = len(config.summary_ids)
                config.total_percentage = total / lines
            else:
                config.total_percentage = 0

    def _compute_name(self):
        day_values = {
            "1": _("Monday"),
            "2": _("Tuesday"),
            "3": _("Wednesday"),
            "4": _("Thursday"),
            "5": _("Friday"),
            "6": _("Saturday"),
            "7": _("Sunday"),
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
                config.day == self.day
                and config.cash_control_config_id.id == self.cash_control_config_id.id
                and config.store_id.id == self.store_id.id
            ):
                raise ValidationError(
                    _("Only one config can exist for that day/cashbox combination per store")
                )

    @api.constrains("summary_ids")
    def constraint_percentage(self):
        for line in self.summary_ids:
            percentage = line.percentage
            if percentage > 100:
                raise ValidationError(
                    _("Product: %s exceeds 100 percent" % line.product_id.name)
                )

    @api.model
    def create(self, vals):
        config_type_product_ids = (
            self.env["cash.control.config.type"]
            .search([("config_ids", "in", [vals["cash_control_config_id"]])])
            .ci_product_ids
        )
        vals["summary_ids"] = [
            (0, 0, {"product_id": product.id}) for product in config_type_product_ids
        ]
        res = super().create(vals)
        return res

    def write(self, vals):
        # constraint won't correctly execute when editing a record and an
        # error message cannot be triggered on compute or it will brick the server
        res = super().write(vals)
        self.constraint_percentage()
        return res

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        user = self.env.user
        # if superadmin, do not apply
        if not self.env.is_superuser():
            args += [
                "|",
                "|",
                ("store_id", "=", False),
                ("store_id", "child_of", [user.store_id.id]),
                ("store_id","in",user.store_ids.ids)
            ]
        return super()._search(
            args, offset, limit, order, count=count, access_rights_uid=access_rights_uid
        )
