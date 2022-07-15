from odoo import models, fields, _
from odoo.exceptions import ValidationError

class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    id_debo = fields.Char(string="Spreadsheet")

    def get_session_by_id_debo(self,id_debo:str,store_id:int) -> models.Model:
        """Finds session record with 'planilla' and store

        Args:
            id_debo (str): Planilla
            store_id (int): store_id.id

        Raises:
            ValidationError: Session not Found
            ValidationError: Multiple sessions found

        Returns:
            models.Model: cash.control.session
        """
        session_id = self.search([('id_debo','=',id_debo),('store_id','=',store_id)])
        if not session_id:
            raise ValidationError(_("Session not found"))
        if len(session_id) > 1:
            raise ValidationError(_("Multiple sessions found with that id debo"))
        return session_id
