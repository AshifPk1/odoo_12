{
    'name': "Cheque Printing Payments",

    'summary': """
        Cheque Printing""",

    'description': """
       Cheque Printing based on BAnks in Payments
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    'category': 'account',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'report/payment_cheque.xml',
        'report/payment_cheque_template.xml',
        'report/report.xml',
        'report/alawwal_template.xml',
        'report/albilad_template.xml',
        'report/alinma_template.xml',
        'report/anb_template.xml',
        'report/jazira_template.xml',
        'report/ncb_template.xml',
        'report/riyad_template.xml',
        'report/sib_template.xml',
        'report/rajhi_template.xml',

    ],
}