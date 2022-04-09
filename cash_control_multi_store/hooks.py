from dateutil.relativedelta import SU
from odoo import api, SUPERUSER_ID

def install_hook(cr, registry):
    '''
    Restores orders in FEP state to previous state, otherwise they end up without state
    and become stuck because PO buttons depend on state
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})

    env.cr.execute('''
    UPDATE cash_control_config
    SET store_id = 1
    WHERE (store_id = '') IS NOT FALSE 
        OR store_id IS NULL
    ''')
    

