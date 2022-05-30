from odoo import models, fields, api


class PartnerNewFields(models.Model):
    _inherit = "res.partner"

    pump = fields.Boolean()
    pump_number = fields.Char()
    checking_account = fields.Selection(
        selection=[("1", "Yes"), ("0", "No")],
        required=True,
        default="0",
    )

    billing_type = fields.Selection(
        selection=[("1", "FT"), ("2", "RE")],
        default="1",
        required=True,
        copy=False,
    )

    group_account = fields.Selection(
        selection=[("1", "Yes"), ("0", "No")],
        copy=False,
    )

    sector_control = fields.Selection(
        selection=[("1", "Yes"), ("0", "No")],
        required=True,
        copy=False,
    )

    block_self_account = fields.Boolean()
    used_voucher_list = fields.Boolean()
    ft_re_notifications = fields.Boolean(string="FT/RE Notifications")
    client_observations = fields.Boolean()
    ignore_auto_block = fields.Boolean()
    lot_service_exception = fields.Boolean()

    def _get_debo_fields(self):
        debo_like_fields = super()._get_debo_fields()
        new_partner_fields = {
            "pump": self.pump,
            "pump_number": self.pump_number,
            "checking_account": self.checking_account,
            "billing_type": self.billing_type,
            "group_account": self.group_account,
            "sector_control": self.sector_control,
            "block_self_account": self.block_self_account,
            "used_voucher_list": self.used_voucher_list,
            "ft_re_notifications": self.ft_re_notifications,
            "client_observations": self.client_observations,
            "ignore_auto_block": self.ignore_auto_block,
            "lot_service_exception": self.lot_service_exception,
        }
        debo_like_fields.update(new_partner_fields)
        return debo_like_fields
