from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    id_debo = fields.Char(string="ID_DEBO")
    # _inherits = {"data.sender": "data_sender_id"}

    # data_sender_id = fields.Many2one(
    #     comodel_name="data.sender",
    #     string="Data Sender",
    #     required=True,
    #     ondelete="cascade",
    #     store=True,
    # )
