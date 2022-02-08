from odoo import fields, models, api

class SalesBody(models.Model):
    _name = 'sales.body'

    # invoice related fields
    type = fields.Selection([('out_invoice', 'Customer Invoice'),('in_invoice', 'Vendor Bill')], string='Invoice Type')#CYV
    AFIP_invoice_type = fields.Selection(['A','B','C','D'],'Invoice Letter')#TIP
    invoice_name = fields.Integer(string='Invoice Number')#NCO
    invoice_line_nbr = fields.Integer(string='Invoice Line Number')#ORD


    #voucher related fields
    voucher_type = fields.Many2one('pos.voucher.type', string='Voucher Type')#TCO
    pos_id = fields.Many2one('pos.pos', string='Point of Sale')#SUC
    voucher_turn = fields.Integer(string='Turn')#TUR
    voucher_sheet = fields.Integer(string='Sheet')#PLA
    voucher_place = fields.Integer(string='Place')#LUG


    #client related fields
    client_number = fields.Integer(string='Client', default=0)#COD
    client_id = fields.Many2one('res.partner', string='Client', compute='add_client_id')#COD

    def _check_client_id(self):
        return True if self.env['res.partner'].search([('id', '=', self.client_id)], limit=1) else False

    def add_client_id(self):
        #aca tendria que checkear si es 0
        if self._check_client_id():
            self.client_id = self.client_number
        else:
            #aca tendria que devolver que hay algo que esta mal con el cliente
            self.client_id = False
        #aca tendria que ir que si es 0 client_id = False (consumidor final anonimo)

    #invoice line related fields
    #product related fields
    product_id = fields.Many2one('product.product', string='Product')#ART
    product_name = fields.Char(string='Product Name')#TIO
    product_category_id = fields.Many2one('product.category', string='Product Category')#RUB
    product_tax_amount = fields.Float(string='Product Tax Amount')#IMI
    product_tax_amount2 = fields.Float(string='Product Tax Amount 2')#IMI2
    product_tax_amount3 = fields.Float(string='Product Tax Amount 3')#IMI3
    quantity = fields.Float(string='Quantity')#CAN

    #price related fields
    unit_price_with_taxes = fields.Float(string='Unit Price')#PUN
    total_amount_with_taxes = fields.Float(string='Total Amount')#NET
    total_amount = fields.Float(string='Total Amount')#NEX
    tax_amount = fields.Float(string='Tax Amount')#IVA
    tax_rate = fields.Float(string='Tax Rate')#TAS_IVA
    unit_price = fields.Float(string='Unit Price')#PUT
    product_cost = fields.Float(string='Product Cost')#COSTO

    

    #fuel related fields
    is_fuel = fields.Boolean(string='Is Fuel')#ESC
    EESS_pump_id = fields.Many2one('eess.pump', string='Pump')#CSU
    DEBO_pump_id = fields.Many2one('debo.pump', string='Pump')#SUR

