from odoo import models,fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    session_complement_percentage = fields.Float(digits=('5','2'))

    #TODO:
    # add to invoice line column_invisible parent.debo_transaction_type != 'complement'