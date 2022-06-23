#This configurations exceed FCO-149 specifications
#Further communication with Foca is needed
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"


    # # c1:
    # ci_minimum_amount = fields.Float(string="Minimum Amount", help="Minimum allowed amount for invoice")
    # ci_maximum_amount = fields.Float(string="Maximum Amount", help="Maximum allowed amount for invoice")

    # #TODO: c2: porcentaje de lo que falta facturar se destine a ese cliente ya que pueden
    # # ser varios los clientes configurados (invoice line field)
    # complement_percentage = fields.Float(digits=(5, 2))
    # #TODO: c3: TURNO en el que aplica ese cliente para FT complemento.
    # config_ids = fields.Many2many(comodel_name='cash.control.config', string="Cashbox")
    # # turn_ids = fields.Many2many(comodel_name="cash.control.turn", string="Turns")
    # #TODO: c4:Día de la semana en que aplica ese cliente
    # ci_monday = fields.Boolean(string="Monday")
    # ci_tueday = fields.Boolean(string="Tuesday")
    # ci_wednesday = fields.Boolean(string="Wednesday")
    # ci_thursday = fields.Boolean(string="Thursday")
    # ci_friday = fields.Boolean(string="Friday")
    # ci_saturday = fields.Boolean(string="Saturday")
    # ci_sunday = fields.Boolean(string="Sunday")
    complement_invoice_config_ids = fields.Many2many(comodel_name="complement.invoice.config", string="Complement Invoice Configurations")
    complement_invoice_config_line_ids = fields.One2many(comodel_name="complement.invoice.config.line", inverse_name="partner_id")
#     Configuracion para realizar automaticamente por dia y turno
# crear turnos delimitando por fecha de inicio/ final
    

    complement_invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="partner_id",
        string="Complement Invoices",
        domain=[('debo_transaction_type','=','complement')]
    )
