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

    is_up_to_date = fields.Boolean(string="Sent to Debo", default=False, compute="_compute_is_up_to_date")
    

    last_update_debo = fields.Datetime(string="Last Update Debo")#, default=_default_last_update_debo
    
    def _compute_is_up_to_date(self):
        for record in self:
            if not record.last_update_debo or record.last_update_debo < record.write_date:
                record.is_up_to_date = False
            else:
                record.is_up_to_date = True

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
            for rule in res.item_ids:
                data_sender.send_debo_fields(
                    data=rule._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
        except Exception as e:
            _logger.error(e)
            raise Warning(e.args)
        return res

    def write(self, vals_list):
        res = super().write(vals_list)
        if res:
            try:
                for rule in self.item_ids:
                    data_sender.send_debo_fields(
                        data=rule._get_debo_fields(),
                        endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                    )
            except Exception as e:
                _logger.error(e)
                raise Warning(e.args)
        return res


class ProductPriceListItem(models.Model):
    _inherit = "product.pricelist.item"

    def _get_debo_fields(self):
        debo_like_fields = {
            "DESCRIPCION": self.pricelist_id.name,
            "ID_CLIENTE_DEBO": self.pricelist_id.env.company.id_debo,
            "CATEGORIA": self._format_categ_id(),
            "PRODUCTO": self.product_id.id if self.product_id else False,
            "FIJO": abs(self.fixed_price),
            "FECHA_VENCIMIENTO": datetime.strftime(
                self.date_end, data_sender._debo_date_format()
            ),
            "ID_DEBO_CLOUD": self.pricelist_id.id,
            "id_debo": self.pricelist_id.id_debo,
            "store_id": self.pricelist_id.store_id.id,
        }
        debo_like_fields.update(self._format_amounts())
        return debo_like_fields

    
    def _format_amounts(self):
        #TODO:
        # "SIGNO" : "+","-","I"
        # "PORCENTAJE" : percent_price or fixed_price 
        # "SIGNO": "-" if self.percent_price >= 0 else "+",
        # "PORCENTAJE": abs(self.percent_price),
        porcentaje = self.percent_price or self.fixed_price
        signo = "I"
        if self.percent_price:
            signo = "-" if porcentaje >= 0 else "+"
        return {
            "SIGNO": signo,
            "PORCENTAJE": abs(porcentaje),
        }
        
    def _format_categ_id(self):
        categ_id = self.categ_id
        if categ_id:
            return [categ_id.id, categ_id.name]
        return []