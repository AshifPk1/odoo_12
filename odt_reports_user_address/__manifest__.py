# -*- coding: utf-8 -*-
{
    'name': "Odt Report User Address",

    'description': """
        Add user address in sale order, quotation and invoice report
    """,

    'author': "OdooTec",
    'website': "www.odootec.com",

    'category': 'Sale',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale',],
    # always loaded
    'data': [
        'report/sale_order_template.xml',
        'report/invoice_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
