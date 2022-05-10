from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

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

    def eventual_document_type(self, code: int = 0) -> int:
        """
        Returns the identification type for the eventual customer
        default :: O (Sigd)
        """
        codes_dict = {
            0: "it_Sigd",
            1: "it_cuit",
            2: "it_CUIL",
            3: "it_dni",
        }
        ref = f"l10n_ar.{codes_dict[code]}"
        it_code = self.env.ref(ref)
        return it_code.id

    def eventual_afip_identification_type(self, code: int = 1) -> int:
        """
        returns the afip identification type for the eventual customer
        default :: 1 (Consumidor Final)
        """
        codes_dict = {
            1: "res_CF",
            2: "res_IVARI",
            3: "res_IVAE",
            4: "res_RM",
            5: "res_EXT",
            6: "res_IVA_LIB",
            7: "res_IVA_NO_ALC",
        }
        ref = f"l10n_ar.{codes_dict[code]}"
        ait_code = self.env.ref(ref)
        return ait_code.id
