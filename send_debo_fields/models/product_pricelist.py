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

    def _get_debo_fields(self) -> dict:
        lines_debo_fields = []
        for line in self.item_ids:
            lines_debo_fields.append(line._get_debo_fields())
        debo_like_fields = {
            "DESCRIPCION": "name",
            "ID_CLIENTE_DEBO": self.env.company.id_debo,
            "REGLAS" : lines_debo_fields,
        }
        return debo_like_fields

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarListaPrecio"

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
    
class ProductPriceListItem(models.Model):
    _inherit = "product.pricelist.item"

    def _get_debo_fields(self):
        debo_like_fields = {
            "CATEGORIA": self.categ_id.id if self.categ_id else False,
            "PRODUCTO": self.product_id.id if self.product_id else False,
            "SIGNO": "-" if self.percent_price >= 0 else "+",
            "PORCENTAJE": self.percent_price,
            "FIJO" : self.fixed_price,
            "FECHA_VENCIMIENTO": datetime.strftime(self.date_end, data_sender._debo_date_format()),
            "ID_DEBO_CLOUD": self.id,
            "id_debo": self.id_debo,
        }
        return debo_like_fields