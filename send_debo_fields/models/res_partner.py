from odoo import models, fields, api, _
from odoo.tools.profiler import profile
from odoo.exceptions import Warning
from datetime import datetime
from ..utils import data_sender
import logging

data_sender = data_sender.DataSender()
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

<<<<<<< HEAD
    id_debo = fields.Char(string="ID_DEBO")

    def test_button(self):
        return data_sender.send_debo_fields(
                data=self._get_debo_fields(),
                endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
            )

=======
>>>>>>> dev_add_send_pricelist
    def _format_vat(self, vat: str) -> str:
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

    def _compute_CTA(self):
        if self.is_company:
            return 0
        else:
            if self.parent_id:
                return self.parent_id.id
            else:
                return 0

    def decode_img_512(self):
        if self.image_512:
            return self.image_512.decode("utf8")
        else:
            return ""

    # @profile
    def _get_debo_fields(self):
        debo_like_fields = {
            "NOM": self.name,
            "DOM": self.street + " " + (self.street2 or "") if self.street else "",
            "CPO": self.zip,
            "LOC": self.city,
            "PCI": self.state_id.ids[0] if len(self.state_id.ids) > 0 else 0,
            "CUIT": self._format_vat(self.vat) or "",
            "TEL": self.phone or 0,
            "FPA": self.property_payment_term_id.id or 0,
            "CTA": self._compute_CTA(),
            "ACT": self.actividades_padron.ids[0]
            if len(self.actividades_padron.ids) > 0
            else 0,  # One2Many en ODOO
            "MOD": self.property_product_pricelist.ids[0]
            if len(self.property_product_pricelist.ids) > 0
            else 0,
            "IVA": self.l10n_ar_afip_responsibility_type_id.ids[0]
            if len(self.l10n_ar_afip_responsibility_type_id.ids) > 0
            else 0,
            "PCX": self.state_id.ids[0] if len(self.actividades_padron.ids) > 0 else 0,
            "VEN": self.user_id.id or 0,
            "FEA": datetime.strftime(self.write_date, data_sender._debo_date_format()),
            "D_EN": 0,  # no existe
            "D_Y": 0,  # no existe
            "NHA": 1 if not self.active else 0,
            "E_HD": 0,  # no existe
            "C_HD": 0,  # no existe
            "ID_LEY": 1,
            "NRO_PER_MAY": self.l10n_ar_gross_income_number or 0,
            "JUR_MAY_PER": self.gross_income_jurisdiction_ids.ids[0]
            if len(self.actividades_padron.ids) > 0
            else 0,  # One2Many en ODOO
            "CLI_CON": self.l10n_ar_gross_income_type,
            "MAIL": self.email or "",
            "TIPO_NOTIFICACION": 0,
            "FEC_CTRL": datetime.strftime(self.sale_order_ids[0].date_order, data_sender._debo_date_format())
            if len(self.sale_order_ids.ids) > 0
            else "",
            "MARCA_SALDO": 0,
            "CONVMULTILATERAL": 1
            if self.l10n_ar_gross_income_type == "multilateral"
            else 0,
            "PAIS": self.country_id.name,
            "aplica_perc_IVA": 1 if self.imp_iva_padron else 0,
            "alicuotas": self._add_alicuot_fields(),
            "IMAGEN": self.decode_img_512(),
            "ID_CLIENTE_DEBO": self.env.company.id_debo,
            "ID_DEBO_CLOUD": self.id,
            "id_debo": self.id_debo,
        }
        # res.update(debo_like_fields)
        return debo_like_fields

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarCliente"

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        try:
            data_sender.send_debo_fields(
                data=res._get_debo_fields(),
                endpoint=f"{res._get_base_endpoint()}{res._get_final_endpoint()}",
            )
        except Exception as e:
            _logger.error(e)
            raise Warning(e.args)
        return res

    def write(self, vals_list):
        res = super().write(vals_list)
        if res:
            try:
                data_sender.send_debo_fields(
                    data=self._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
            except Exception as e:
                _logger.error(e)
                raise Warning(e.args)
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
