# -*- coding: utf-8 -*-
{
    'name': 'Cash Control Multi-store',
    'summary': """Add multi-store capability to cash control""",
    'version': '13.0.0.0.1',
    'author': 'Calyx Servicios S.A.',
    'license': 'LGPL-3',
    'category': 'cash_control',
    'depends': [
        'sale_multi_store',
        'account_multi_store',
        'cash_control',
    ],
    'data': [
        'security/security.xml',
        'views/account_journal_view.xml',
        'views/cash_control_config_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'install_hook' : 'install_hook',
}
