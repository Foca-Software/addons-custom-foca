from odoo import models, fields, api, _
from odoo.tools.profiler import profile
import json
import logging
import requests
from datetime import datetime
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def send_debo_fields(self, method="create"):
        #TODO: create debo config model?
        # url = self.env['debo.config'].search([('model_id','=',)], limit=1).url
        method_endpoints = {
            'create' : '/guardarCliente',
            'write' : '/guardarCliente',
        }
        try:
            headers = {"Authorization" : "none",
                    "Content-Type" : "application/json",
                    "Accept" : "*/*"}
            data = self.get_debo_fields()
            if not self.env.company.debo_cloud_url:
                raise Warning('No se ha configurado la URL de Debo Cloud')
            url = self.env.company.debo_cloud_url + method_endpoints[method]
            r = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(data),
                verify=True
            )
        except Exception as e:
            raise Warning(e)
        try:
            response = r.text
            _logger.info(response)
        except Exception as e:
            raise Warning(e.args)

        return True

    def _format_vat(self, vat : str) -> str:
        if not vat:
            return False
        vat_type = self.l10n_latam_identification_type_id.name
        if vat_type == "CUIT":
            vat = f"{vat[0:2]}-{vat[2:10]}-{vat[-1]}"
        elif vat_type == "DNI":
            vat = f"00-{vat}-0"
        return vat

    def _add_alicuot_fields(self) -> dict:
        alicuot_fields = {
            "PERC": False,
            "POR_RED": False,
            "PER_SL": False,
            "PERC_PORC": False,
            "PER_IVARG17": False,
            "PER_ATER": False,
            "OpJurMis": False,
            "TIPO_RES_60": False,
            "TipAlij19": False,
            "SL_Concep": False,
            "SL_TSuj": False,
        }
        fields = [
            "id",
            "tag_id",
            "alicuota_percepcion",
            "alicuota_retencion",
            "withholding_amount_type",
        ]
        return self.arba_alicuot_ids.read(fields)

    # @profile
    def get_debo_fields(self):
        debo_like_fields = {
            "NOM": self.name,
            "DOM": self.street + " " + (self.street2 or ""),
            "CPO": self.zip,
            "LOC": self.city,
            "PCI": self.state_id.ids,
            "CUIT": self._format_vat(self.vat) or "",
            "TEL": self.phone or 0,
            "FPA": self.property_payment_term_id.id or 0,
            "CTA": self.parent_id.id if not self.is_company else self.id,
            "ACT": self.actividades_padron.ids[0] or 0,  # One2Many en ODOO
            "MOD": self.property_product_pricelist.ids[0] or 0,
            "IVA": self.l10n_ar_afip_responsibility_type_id.ids[0] or 0,
            "PCX": self.state_id.ids[0] or 0,
            "VEN": self.user_id.id or 0,
            "FEA": datetime.strftime(self.write_date, "%d/%m/%Y"),
            "D_EN": 0,  # no existe
            "D_Y": 0,  # no existe
            "NHA": 1 if not self.active else 0,
            "E_HD": 0,  # no existe
            "C_HD": 0,  # no existe
            "ID_LEY": 1,
            "NRO_PER_MAY": self.l10n_ar_gross_income_number or 0,
            "JUR_MAY_PER": self.gross_income_jurisdiction_ids.ids[0] or 0,  # One2Many en ODOO
            "CLI_CON": self.l10n_ar_gross_income_type,
            "MAIL": self.email or '',
            "TIPO_NOTIFICACION": 0,
            "FEC_CTRL": self.sale_order_ids[0].confirmation_date
            if len(self.sale_order_ids.ids) > 0
            else "",
            "MARCA_SALDO": 0,
            "CONVMULTILATERAL": 1
            if self.l10n_ar_gross_income_type == "multilateral"
            else 0,
            "PAIS": self.country_id.name,
            "aplica_perc_IVA": 1 if self.imp_iva_padron else 0,
            "alicuotas": self._add_alicuot_fields(),
            "ID_DEBO_CLOUD": self.id,
            "ID_CLIENTE_DEBO" : self.company_id.id
        }
        return debo_like_fields

    @api.model
    def create(self,vals_list):
        res = super().create(vals_list)
        try:
            res.send_debo_fields('create')
        except Exception as e:
            return e.args
        return res

    def write(self, vals_list):
        res = super().write(vals_list)
        _logger.info(res)
        if res:
            try:
                self.send_debo_fields('write')
            except Exception as e:
                return e.args
        return res

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
