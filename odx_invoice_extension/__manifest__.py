# -*- coding: utf-8 -*-
{
    'name': "Invoice Print extension",
    'summary': "Invoice Print extension",
    'description': """Terms and Conditions  and Payment Details in invoice print """,
    'author': "Odox SoftHub",
    'category': 'account',
    'depends': ['base', 'account','odx_bank_details_pricelist'],
    'data': [
        'report/report_invoice_document_inherit.xml'
    ],

}
