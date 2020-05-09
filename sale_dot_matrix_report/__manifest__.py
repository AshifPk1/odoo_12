# Copyright 2018 QubiQ (http://www.qubiq.es)
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': ' Sale Report',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': '',
    'website': '',
    'license': 'AGPL-3',
    'summary': '',
    'depends': [
        'sale', 'sale_triple_discount'
    ],
    'data': [
        'report/sale_report_template.xml',
        'report/report.xml',
        'report/layout.xml'
    ],
    'installable': True,

}
