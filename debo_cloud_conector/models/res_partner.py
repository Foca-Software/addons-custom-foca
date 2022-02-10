from odoo import models, fields, api, _
from odoo.tools.profiler import profile
import json
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def send_debo_fields(self):
        pass

    def _format_vat(self,vat):
        vat_type = self.l10n_latam_identification_type_id.name
        if vat_type == "CUIT":
            vat = f"{vat[0:2]}-{vat[2:10]}-{vat[-1]}"
        elif vat_type == "DNI":
            vat = f"00-{vat}-0"
        return vat

    @profile
    def get_debo_fields(self):
        debo_like_fields = {
            "NOM" : self.name,
            "DOM" : self.street + " " + (self.street2 or ""),
            "CPO" : self.zip,
            "LOC" : self.city,
            "PCI" : self.state_id.ids,
            "CUIT" : self._format_vat(self.vat),
            "TEL" : self.phone,
            "ACT" : self.actividades_padron.ids, #One2Many en ODOO
            "MOD" : self.property_product_pricelist.ids,
            "IVA" : self.l10n_ar_afip_responsibility_type_id.ids,
            "PCX" : self.state_id.ids,
            "VEN" : self.user_id.id,
            "D_EN" : False, #no existe
            "D_Y" : False, #no existe
            "NRO_PER_MAY" : self.l10n_ar_gross_income_number,
            "JUR_MAY_PER" : self.gross_income_jurisdiction_ids.ids,#One2Many en ODOO
            "MAIL" : self.email,
            "CONVMULTILATERAL" : 1 if self.l10n_ar_gross_income_type == "multilateral" else 0,
            "PAIS" : self.country_id.name,
            "idDeboCloud" : self.id,
        }
        _logger.warn(json.dumps(debo_like_fields))
        # _logger.info(self.l10n_latam_identification_type_id.read())
        return debo_like_fields

# unused
    # def _necessary_fields(self):
    #     fields = [
    #         "name",
    #         "street",
    #         "street2",
    #         "zip",
    #         "city",
    #         "state_id",
    #         "vat",
    #         "phone",
    #         "property_payment_term_id",
    #         "actividades_padron",
    #         "property_product_pricelist",
    #         "l10n_ar_afip_responsibility_type_id",
    #         "user_id",
    #         "email",
    #         "l10n_ar_gross_income_type",
    #         "l10n_ar_gross_income_number",
    #         "gross_income_jurisdiction_ids",
    #         "country_id",
    #         "id",
    #     ]
    #     return fields

    # @profile
    # def get_debo_fields(self):
    #     fields_dict = self.read(self._necessary_fields)[0]
    #     debo_like_fields = {
    #         "NOM" : fields_dict["name"],
    #         "DOM" : fields_dict["street"] + " " + (fields_dict["street2"] or ""),
    #         "CPO" : fields_dict["zip"],
    #         "LOC" : fields_dict["city"],
    #         "PCI" : fields_dict["state_id"][1],
    #         "CUIT" : self._format_vat(fields_dict["vat"]),
    #         "TEL" : fields_dict["phone"],
    #         "ACT" : fields_dict["actividades_padron"], #One2Many en ODOO
    #         "MOD" : fields_dict["property_product_pricelist"][0],
    #         "IVA" : fields_dict["l10n_ar_afip_responsibility_type_id"][0],
    #         "PCX" : fields_dict["state_id"][0],
    #         "VEN" : fields_dict["user_id"],
    #         "D_EN" : False, #no existe
    #         "D_Y" : False, #no existe
    #         "NRO_PER_MAY" : fields_dict["l10n_ar_gross_income_number"],
    #         "JUR_MAY_PER" : fields_dict["gross_income_jurisdiction_ids"],#One2Many en ODOO
    #         "MAIL" : fields_dict["email"],
    #         "CONVMULTILATERAL" : fields_dict["l10n_ar_gross_income_type"] == "multilateral",
    #         "PAIS" : fields_dict["country_id"][1],
    #         "idDeboCloud" : fields_dict["id"],
    #     }
    #     _logger.warn(json.dumps(fields_dict))
    #     _logger.warn(json.dumps(debo_like_fields))