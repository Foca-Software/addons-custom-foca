from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    id_debo_p = fields.Char(string="ID_DEBO Supplier")
    id_debo_c = fields.Char(string="ID_DEBO Customer")
    eventual_customer = fields.Boolean(string="Eventual Customer", default=False)

    # can_have_check_account = fields.Boolean(string="Check Account", default=False)
    # oil_card = fields.Selection(selection=[("invoice","Invoice"),("remittance","Remittance")],string="Oil Card",)