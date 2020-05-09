import xlwt
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class SalePersonPrint(models.AbstractModel):
    _name = 'report.sale_person_report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):




        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14})
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 14})
        bold = workbook.add_format({'bold': True})
        worksheet = workbook.add_worksheet("Product Balance Report")
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_column('K:K', 17)
        worksheet.set_column('L:L', 22)
        worksheet.set_column('M:M', 17)
        worksheet.set_column('N:N', 17)


        # worksheet.set_column('U:U', 30)
        end_col = 17
        workbook = xlwt.Workbook()
        worksheet.merge_range(0, 0, 1, 13, 'Sale Report(Based On Sales Rep)', heading_format)
        # worksheet.merge_range('A:S',"Sale Report(Based On Sales Rep)", heading_format)
        worksheet.write(2, 0, 'Salesman', heading_format)
        worksheet.write(2, 1, 'Location', heading_format)
        worksheet.write(2, 2, 'Clients', heading_format)
        worksheet.write(2, 3, 'Years', heading_format)
        worksheet.write(2, 4, 'Quarter', heading_format)
        worksheet.write(2, 5, 'Month', heading_format)
        worksheet.write(2, 6, 'Date', heading_format)
        worksheet.write(2, 7, 'Code', heading_format)
        worksheet.write(2, 8, 'Product Name', heading_format)
        worksheet.write(2, 9, 'Product Segmentation', heading_format)
        worksheet.write(2, 10, 'Quantity', heading_format)
        worksheet.write(2, 11, 'Price without tax', heading_format)
        worksheet.write(2, 12, 'Price with tax', heading_format)
        worksheet.write(2, 13, 'Gross Margin', heading_format)
        row =3

        from_date = str(wiz.from_date)+' '+'00:00:00'
        to_date = str(wiz.to_date) + ' ' + '23:23:59'
        if wiz.from_date and wiz.to_date:
            sale_orders = self.env['sale.order'].search([('confirmation_date','>=',from_date),
                                                         ('confirmation_date', '<=', to_date),
                                                         ('state', '=', 'sale')])
        product_type = {'consu': 'Consumable', 'service': 'Service', 'product': 'Storable Product'}
        for sale_order in sale_orders:
            for line in sale_order.order_line:
                gross_total = line.price_subtotal - (line.product_uom_qty*line.product_id.standard_price)
                date = fields.Datetime.from_string(line.order_id.confirmation_date)
                if date.month >= 1 and date.month <=3:
                    quarter = 'Q1'
                elif date.month >= 4 and date.month <= 6:
                    quarter = 'Q2'
                elif date.month >= 7 and date.month <= 9:
                    quarter = 'Q3'
                else:
                    quarter = 'Q4'

                worksheet.write(row, 0, line.order_id.user_id.name)
                worksheet.write(row, 1, sale_order.team_id.name)
                worksheet.write(row, 2, line.order_id.partner_id.name)
                worksheet.write(row, 3, date.year)
                worksheet.write(row, 4, quarter)
                worksheet.write(row, 5, date.month)
                worksheet.write(row, 6, date.day)
                worksheet.write(row, 7, line.product_id.default_code )
                worksheet.write(row, 8, line.product_id.name)
                worksheet.write(row, 9, product_type[line.product_id.type])
                worksheet.write(row, 10, line.product_uom_qty)
                worksheet.write(row, 11, round(line.price_subtotal,2))
                worksheet.write(row, 12, round(line.price_total,2))
                worksheet.write(row, 13, round(gross_total,2))
                row +=1
