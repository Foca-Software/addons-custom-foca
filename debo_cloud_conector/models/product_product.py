from odoo import models, fields, api, _
from odoo.tools.profiler import profile
from odoo.exceptions import Warning
from datetime import datetime
import base64
import json
import logging
import requests
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    id_debo = fields.Char(string="ID Debo")

    @api.depends('lst_price', 'taxes_id')
    def _calculate_PreVen(self, lst_price: float, taxes_id: list) -> float:
        percent = 0
        fixed = 0
        for tax in taxes_id:
            if tax.amount_type == "percent":
                percent += tax.amount
            else:
                fixed += tax.amount
        if percent and percent > 0:
            percent *= 0.01
            return lst_price / (1 + percent) - fixed
        else:
            return lst_price - fixed

    def _calculate_taxes(self, taxes) -> list:
        necessary_tax_fields = [
            "id",
            "name",
            "amount",
            "amount_type",
            "id_debo",
        ]
        return taxes.read(necessary_tax_fields)

    def _calculate_category(self) -> list or 0:
        necessary_category_fields = [
            "id",
            "name",
            "id_debo",
        ]
        try:
            return self.categ_id.read(necessary_category_fields)[0]
        except Exception as e:
            _logger.error(e)
            return 0

    def _calculate_bom_fields(self) -> dict:
        dictionary = {}
        # es kit?
        is_kit = self.env["mrp.bom"].search([("product_id", "=", self.id)])
        dictionary["PRO"] = 1 if is_kit else 0
        # es parte de un kit?
        is_part_of_kit = self.env["mrp.bom.line"].search(
            [("product_id", "=", self.id), ("bom_id.type", "=", "phantom")]
        )
        dictionary["FPP"] = 1 if is_part_of_kit else 0
        # es materia prima
        is_ingredient = self.env["mrp.bom.line"].search(
            [("product_id", "=", self.id), ("bom_id.type", "=", "normal")]
        )
        dictionary["CLA"] = 5 if is_ingredient else 0
        return dictionary

    def decode_img(self):
        if self.image_512:
            return self.image_512.decode("utf8")
        else:
            return ""
    # @profile
    def get_debo_fields(self) -> dict:
        Taxes = self._calculate_taxes(self.taxes_id)
        PreNet = self._calculate_PreVen(self.lst_price, self.taxes_id)
        debo_like_fields = {
            "DetArt": self.name,
            "Categ": self._calculate_category(),
            "Costo": self.standard_price or 0,
            "PreNet": round(PreNet,2),
            "Taxes": Taxes,
            "UniVen": self.uom_id.ids[0] if len(self.uom_id.ids) > 0 else 0,
            "UltAct": datetime.strftime(self.write_date, "%d/%m/%Y"),
            "CodPro": self.seller_ids.ids[0] if len(self.seller_ids.ids) > 0 else 0,
            "ExiDep": self.qty_available,
            "PreVen": self.lst_price or 0,
            "TIP": self.type,
            "ESS": 1 if self.type == "service" else 0,
            "NHA": 0 if self.active else 1,
            "DET_LAR": self.display_name or "",
            "IMP_IMP_INT": 1 if len(Taxes) > 0 else 0,
            "LISPSD": self.pricelist_id.read(),
            "E_HD": "",
            "C_HD": "",
            "E_HD1": "",
            "C_HD1": "",
            "E_HD2": "",
            "C_HD2": "",
            "CODBAR" : self.barcode or "",
            "IMAGEN" : self.decode_img(),
            "ID_DEBO_CLOUD": self.id,
            "ID_CLIENTE_DEBO" : self.env.company.id,
            "id_debo": self.id_debo,
        }
        debo_like_fields.update(self._calculate_bom_fields())
        return debo_like_fields

    def send_debo_fields(self, method="create"):
        #TODO: create debo config model?
        # url = self.env['debo.config'].search([('model_id','=',)], limit=1).url
        method_endpoints = {
            'create' : '/guardarProducto',
            'write' : '/guardarProducto',
        }
        if self._context.get('import_file',False):
            return False
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
            _logger.error(e)
            raise Warning(e)
        try:
            response = r.text
            _logger.info(response)
        except Exception as e:
            _logger.error(e)
            raise Warning(e.args)

        return True

    @api.model
    def create(self,vals_list):
        res = super().create(vals_list)
        try:
            res.send_debo_fields('create')
        except Exception as e:
            _logger.error(e.args)
            raise Warning("Error sending data to DEBO, please try again later")
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

# def _necessary_fields(self) -> list:
#     """
#     Return the fields that are necessary to send to DEBO
#     """
#     fields = [
#         "name",  # DetArt
#         "categ_id",  # CodRub
#         "product_tmpl_id",
#         "standard_price",  # Precio
#         "lst_price",  # PreNet
#         "taxes_id",  # ImpInt
#         "uom_id",  # UniVen
#         "__last_update",  # UltAct
#         "seller_ids",  # CodPro
#         "type",
#         "display_name",  # DET_LAR
#         "active",  # NHA
#         "id",  # ID_DEBO_CLOUD
#         "qty_available",  # ExiDep
#     ]
#     return fields
# fields = self._necessary_fields()
# fields_dict = self.read(fields)[0]
# PreVen = self._calculate_PreVen(
#     fields_dict["lst_price"], fields_dict["taxes_id"]
# )
# ExiDep = self._calculate_ExiDep(fields_dict["lst_price"], fields_dict["qty_available"])
# debo_like_fields = {
#     "DetArt": fields_dict["name"],
#     "CodRub": fields_dict["categ_id"][0],
#     "Costo": fields_dict["standard_price"],
#     "PreNet": fields_dict["lst_price"],
#     "ImpInt": taxes,
#     "UniVen": fields_dict["uom_id"][0],
#     "UltAct": datetime.strftime(fields_dict["__last_update"], "%d/%m/%Y"),
#     "ALT" : datetime.strftime(self.write_date, "%d/%m/%Y"),
#     "CodPro": fields_dict["seller_ids"],
#     "ExiDep": ExiDep,
#     "PreVen": PreVen,
#     "TIP": fields_dict["type"],
#     "ESS": 1 if fields_dict["type"] == "service" else 0,
#     "NHA": 0 if fields_dict["active"] else 1,
#     "DET_LAR": fields_dict["display_name"],
#     "ID_DEBO_CLOUD": fields_dict["id"],
# }
