from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit="res.partner"

    eventual_customer = fields.Boolean(string="Eventual Customer", default=False)

    @api.model
    def create_eventual(self, vals: dict) -> object:
        """
        Creates a copy of default 'end customer' as a new eventual customer
        return :: res_partner object
        """
        cfa = self.env.ref("l10n_ar.par_cfa")
        eventual_customer = cfa.copy()
        eventual_customer.write(vals)
        return eventual_customer