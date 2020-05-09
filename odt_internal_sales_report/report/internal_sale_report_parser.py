from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import date,timedelta,datetime
from odoo.tools.float_utils import float_round

class InternalSaleReportWizardParser(models.AbstractModel):
    _name = 'report.odt_internal_sales_report.report_internal_sale_report'

    def sale_order(self, data,analytic_account):
        # analytic_account = (
        #         self.env['account.analytic.account'].search([('id', '=', analytic_account)])).id

        if not data.get('date_from') and not data.get('date_to'):
            orders = self.env['sale.order'].search(
                [('state', '=', 'done'), ('analytic_account_id', '=', analytic_account.id)])

        elif data.get('date_from') and not data.get('date_to'):
            orders = self.env['sale.order'].search(
                [('confirmation_date', '>=', data.get('date_from')), ('state', '=', 'done'),
                 ('analytic_account_id', '=', analytic_account.id)])


        elif data.get('date_to') and not data.get('date_from'):
            orders = self.env['sale.order'].search(
                [('confirmation_date', '<=', data.get('date_to')), ('state', '=', 'done'),
                 ('analytic_account_id', '=', analytic_account.id)])
        else:
            orders = self.env['sale.order'].search(
                [('confirmation_date', '<=', data.get('date_to')), ('confirmation_date', '>=', data.get('date_from')),
                 ('state', '=', 'done'), ('analytic_account_id', '=', analytic_account.id)])
        print(orders)
        return orders

    @api.multi
    def _get_report_values(self, docids, data=None):
        invoice_list = []
        if data.get('analytic_account'):
            analytic_account=(self.env['account.analytic.account'].search([('id','in',data.get('analytic_account'))])).ids
            data['analytic_account']=self.env['account.analytic.account'].search([('id','in',data.get('analytic_account'))])
        else:
            analytic_account=(self.env['account.analytic.account'].search([])).ids

        if not data.get('date_from') and not data.get('date_to'):
            orders=self.env['sale.order'].search([('state','=','done'),('analytic_account_id','in',analytic_account)])
            if not data.get('analytic_account'):
                orders = self.env['sale.order'].search(
                    [('state', '=', 'done')])
            invoices=self.env['account.invoice'].search([('state','in',('open','done')),('type','=','out_invoice')])
            if orders:
                for order in orders:
                    for invoice in invoices:
                        if invoice.id not in order.invoice_ids.ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
            else:
                for invoice in invoices:
                        invoice_list.append(invoice)

        elif data.get('date_from') and not data.get('date_to'):
            orders = self.env['sale.order'].search([('confirmation_date','>=',data.get('date_from')),('state','=','done'),('analytic_account_id','in',analytic_account)])
            invoices = self.env['account.invoice'].search([('date_invoice','>=',data.get('date_from')),('state', 'in', ('open', 'done')),('type','=','out_invoice')])
            if not data.get('analytic_account'):
                orders = self.env['sale.order'].search(
                    [('confirmation_date', '>=', data.get('date_from')), ('state', '=', 'done')])

            if orders:
                for order in orders:
                    for invoice in invoices:
                        if invoice.id not in order.invoice_ids.ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
            else:
                for invoice in invoices:
                        invoice_list.append(invoice)

        elif data.get('date_to') and not data.get('date_from'):
            orders = self.env['sale.order'].search(
                [('confirmation_date', '<=', data.get('date_to')), ('state','=','done'),('analytic_account_id','in',analytic_account)])
            invoices = self.env['account.invoice'].search([('date_invoice','<=',data.get('date_to')),('state', 'in', ('open', 'done')),('type','=','out_invoice')])
            if not data.get('analytic_account'):
                orders = self.env['sale.order'].search(
                    [('confirmation_date', '<=', data.get('date_to')), ('state', '=', 'done')])

            if orders:
                for order in orders:
                    for invoice in invoices:
                        if invoice.id not in order.invoice_ids.ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
            else:
                for invoice in invoices:
                        invoice_list.append(invoice)

        else:
            orders = self.env['sale.order'].search(
                [('confirmation_date', '<=', data.get('date_to')),('confirmation_date', '>=', data.get('date_from')),('state','=','done'),('analytic_account_id','in',analytic_account)])
            invoices = self.env['account.invoice'].search([('date_invoice','>=',data.get('date_from')),('state', 'in', ('open', 'done')),('type','=','out_invoice')])
            if not data.get('analytic_account'):
                orders = self.env['sale.order'].search(
                    [('confirmation_date', '<=', data.get('date_to')),
                     ('confirmation_date', '>=', data.get('date_from')), ('state', '=', 'done')])

            if orders:
                for order in orders:
                    for invoice in invoices:
                        if invoice.id not in order.invoice_ids.ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
            else:
                for invoice in invoices:
                        invoice_list.append(invoice)
        if data.get('need_invoices_without_so')==True:
            invoice_list=invoice_list
        else:
            invoice_list=False
        return {
                'docs': orders,
                'sale_orders': self.sale_order,
                'invoices':invoice_list,
                'data':data
            }