# -*- coding: utf-8 -*-
{
    'name': 'VERI*FACTU Fecha Operacion',
    'version': '15.0.0.1',
    'category': 'Accounting & Finance',
    'description': """
Incorpora la fecha operación (Fecha Contable) en el envío a VERI*FACTU
Bloquea el campo ¿Fallido?, para que no se pueda desmarcar
    """,
    'author': 'Infobit Informática',
    "license": "AGPL-3",
    'depends': [
        'l10n_es_verifactu_oca', 'account'
    ],
    'init_xml': [],
    'update_xml': [
       'views/account_move.xml',
       'report/report_invoice.xml',
    ],
    'demo_xml': [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
