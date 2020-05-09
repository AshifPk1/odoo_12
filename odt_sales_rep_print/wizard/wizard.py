from odoo import fields, models, api,_
from odoo.exceptions import  UserError


class SaleRepReport(models.TransientModel):
    _name = 'sale.rep.report'
    _description = 'Sales Person Report Wizard'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    report_type = fields.Selection([
            ('pdf','PDF'),
            ('excel', 'EXCEL'),
        ], string='Report Type', default='excel')

    @api.multi
    def action_print_rep(self):
        if self.from_date > self.to_date:
            raise UserError("'To Date' is lesser than 'From Date'.Please check the date")
        if self.report_type == 'excel':
            data = {}
            return self.env.ref('odt_sales_rep_print.sale_person_report_xlsx').report_action(self, data=data)
        else:
            data = {'from_date':self.from_date,'to_date':self.to_date}
            return self.env.ref('odt_sales_rep_print.sale_person_report_pdf').report_action(self,data=data)

    @api.multi
    def action_print_review(self):
        if self.from_date > self.to_date:
            raise UserError("'To Date' is lesser than 'From Date'.Please check the date")
        if self.report_type == 'pdf':
            data = {'from_date': self.from_date, 'to_date': self.to_date}
            return self.env.ref('odt_sales_rep_print.sale_person_report_pdf_review').report_action(self, data=data)





