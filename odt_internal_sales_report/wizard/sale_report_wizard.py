from odoo import models, fields, api
from datetime import datetime, date


class ProductBalanceReport(models.TransientModel):
    _name = 'internal.sale.report'

    date_from=fields.Datetime('Date From')
    date_to=fields.Datetime('Date To')
    analytic_account_ids=fields.Many2many('account.analytic.account',string='Analytic Account')
    include_invoices_without_so=fields.Boolean('Invoices Without SO')
    show_total=fields.Boolean('Show Total Only')

    @api.multi
    def print_confirm(self):

        data = {
            'date_from':self.date_from,
            'date_to': self.date_to,
            'analytic_account':self.analytic_account_ids.ids,
            'need_invoices_without_so':self.include_invoices_without_so,
            'show_total':self.show_total,
        }
        return self.env.ref('odt_internal_sales_report.report_internal_sale').report_action([], data=data)
        # return self.env.ref('odt_internal_sales_report.report_internal_sale_report').report_action(self, data=data)