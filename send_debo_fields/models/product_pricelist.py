from odoo import models, fields, api, _
from odoo.tools.profiler import profile
from odoo.exceptions import Warning
from datetime import datetime
import base64
import json
import logging
import requests
from ..utils import data_sender

data_sender = data_sender.DataSender()
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.pricelist"



{
    "DESCRIPCION": "lista de prueba", name
    "CATEGORIA": [1234, "lista de mentira"],
    "PRODUCTO": 1,
    "SIGNO": "+",
    "PORCENTAJE": 50,
    "FECHA_VENCIMIENTO": "10/10/20222", date_end
    "ID_DEBO_CLOUD": 1,
    "ID_CLIENTE_DEBO": 1,
    "id_debo": 1
} 

    def _get_debo_fields(self) -> dict:
        Taxes = self._calculate_taxes(self.taxes_id)
        PreNet = self._calculate_PreVen(self.lst_price, self.taxes_id)
        debo_like_fields = {
            "ID_CLIENTE_DEBO": self.env.company.id_debo,
            "ID_DEBO_CLOUD": self.id,
            "id_debo" : self.id_debo,
        }
        debo_like_fields.update(self._calculate_bom_fields())
        return debo_like_fields

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarProducto"

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        try:
            data_sender.send_debo_fields(
                data=res._get_debo_fields(),
                endpoint=f'{res._get_base_endpoint()}{res._get_final_endpoint()}',
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
                    endpoint=f'{self._get_base_endpoint()}{self._get_final_endpoint()}',
                )
            except Exception as e:
                _logger.error(e)
                raise Warning(e.args)
        return res
    
