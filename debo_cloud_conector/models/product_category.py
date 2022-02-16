from attr import fields_dict
from odoo import models, fields, api, _
from odoo.tools.profiler import profile
from datetime import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.category"

    def _get_debo_fields(self):
        return {
            "ID_DEBO_CLOUD" : self.id,
            "NOM": self.name,
        }
    
    def _send_debo_fields(self):
        fields = self._get_debo_fields()
        #TODO: connect to debo endpoint
        return True

    def create(self,vals_list):
        res = super().create(vals_list)
        try:
            res._send_debo_fields()
        except Exception as e:
            return e.args
        return res