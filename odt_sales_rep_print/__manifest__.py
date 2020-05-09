{
    'name': 'SALE REP PRINT',
    'author': "odootec",
    'description': " ",
    'depends': ['base', 'sale','report_xlsx'],
    'data': [
        'report/sale_person_report_template.xml',
        'report/report.xml',
        'views/sale_rep_wizard.xml',
            ],
    'installable': True,
    'auto_install': False,
}