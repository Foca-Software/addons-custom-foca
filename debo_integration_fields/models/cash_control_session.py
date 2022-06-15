from odoo import models, fields, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    id_debo = fields.Char(string="Spreadsheet")

    def get_session_by_id_debo(self,id_debo:str) -> models.Model:
        session_id = self.search([('id_debo','=',id_debo)])
        if not session_id:
            raise ValidationError(_("Session not found"))
        if len(session_id) > 1:
            _logger.error(session_id)
            raise ValidationError(_("Multiple sessions found with that id debo"))
        return session_id
