from odoo import models, fields, api


class PartnerNewFields(models.Model):
    _inherit = "res.partner"

    pump = fields.Boolean()
    pump_number = fields.Char()
    checking_account = fields.Boolean(required=True,
                                        default=False)

    billing_type = fields.Selection(selection=[("1","FT"),
                                                ("2","RE")],
                                    default="1",
                                    required=True,
                                    copy=False )

    group_account = fields.Selection(selection=[("1","Yes"),
                                                ("0", "No")],
                                                copy=False)

    sector_control = fields.Selection(selection=[("1","Yes"),
                                                ("0", "No")],
                                                copy=False)

    block_self_account = fields.Boolean()
    used_voucher_list = fields.Boolean()
    ft_re_notifications = fields.Boolean(string="FT/RE Notifications")
    client_observations = fields.Boolean()
    ignore_auto_block = fields.Boolean()
    lot_service_exception = fields.Boolean()
