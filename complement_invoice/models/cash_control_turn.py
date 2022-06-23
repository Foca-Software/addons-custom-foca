from odoo import api, fields, models, _ 
from odoo.exceptions import ValidationError

class CashControlTurn(models.Model):
    _name = "cash.control.turn"
    _description = "Cash Control Turn"

    name = fields.Char(string="Name")

    start_time = fields.Float(string="Start Time")#digits=(4, 2), 
    end_time = fields.Float(string="End Time")#digits=(4, 2), 

    session_ids = fields.One2many(comodel_name='cash.control.session',inverse_name='turn_id', string="Sessions")


    @api.constrains('start_time','end_time')
    def _constraint_time(self):
        if self.start_time < 0 or self.start_time > 24 \
            or self.end_time < 0 or self.end_time > 24:
            raise ValidationError(_("Time must be greater than 0 and lesser than 24"))