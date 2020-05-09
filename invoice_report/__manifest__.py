# Copyright 2018 QubiQ (http://www.qubiq.es)
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': ' Invoice Report',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': '',
    'website': '',
    'license': 'AGPL-3',
    'summary': '',
    'depends': [
        'account', 'account_invoice_triple_discount'
    ],
    'data': [
        'report/invoice_report_template.xml',
        'report/report.xml',
        'report/layout.xml'
    ],
    'installable': True,

}
