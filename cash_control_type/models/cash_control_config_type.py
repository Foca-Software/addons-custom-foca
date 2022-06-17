from odoo import models, fields, api


class CashControlConfigType(models.Model):
    _name = "cash.control.config.type"
    _description = "Cash Control Config Type"

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")

    place_of_sale = fields.Selection(
        string="Place of Sale",
        selection=[("fuel_lot", "Fuel Lot"), ("shop", "Shop"), ("box", "Box")],
        required=True,
    )

    sells_fuel = fields.Boolean()
    uses_complement_invoice = fields.Boolean()
    creates_complement_invoice_in_pos = fields.Boolean()
    creates_complement_invoice_in_cloud = fields.Boolean()

    config_ids = fields.One2many(comodel_name='cash.control.config', inverse_name='type_id', string='Cashboxs')
    

    @api.onchange('place_of_sale')
    def _onchange_place_of_sale(self):
        self.sells_fuel = self.place_of_sale in self._fuel_selling_places()

    def _fuel_selling_places(self):
        return ['fuel_lot']
    
    #TODO:
    #New fields will be needed for type shop. For now is_shop_cashbox is computed in config