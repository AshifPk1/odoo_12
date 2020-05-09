from odoo import models, fields
import datetime
import io
import base64

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class StoreReport(models.AbstractModel):
    _name = 'report.store.report.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def calculate_discount_amount(self, line, disc_no):
        price = 0.0
        amount = 0.0
        discount = discount2 = discount3 = discount4 = 0.00
        disc_per = disc_per2 = disc_per3 = disc_per4 = 0.0
        amount = line.price_unit

        if line.discount1:
            if '%' not in str(line.discount1):
                discount = float(line.discount1) / line.product_uom_qty
            else:
                disc_str = str(line.discount1).replace(' ', '')
                disc_per = (disc_str.split('%')[0])
        if line.discount2:
            if '%' not in str(line.discount2):
                discount2 = float(line.discount2) / line.product_uom_qty
            else:
                disc_str2 = str(line.discount2).replace(' ', '')
                disc_per2 = (disc_str2.split('%')[0])
        if line.discount3:
            if '%' not in str(line.discount3):
                discount3 = float(line.discount3) / line.product_uom_qty
            else:
                disc_str3 = str(line.discount3).replace(' ', '')
                disc_per3 = (disc_str3.split('%')[0])
        if line.discount4:
            if '%' not in str(line.discount4):
                discount4 = float(line.discount4) / line.product_uom_qty
            else:
                disc_str4 = str(line.discount4).replace(' ', '')
                disc_per4 = (disc_str4.split('%')[0])

        if disc_no == 1:
            price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price = price - (float(discount))
            return round((amount - price) * line.product_uom_qty, 2)
        if disc_no == 2:
            amt1 = amt2 = 0
            price = line.price_unit
            if line.discount1:
                price = price * (1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
            amt1 = amount - price
            price *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price = price - (float(discount2))
            amt2 = amount - amt1 - price
            return round(amt2 * line.product_uom_qty, 2)
        if disc_no == 3:
            amt1 = amt2 = amt3 = 0
            price = line.price_unit
            if line.discount1:
                price = price * (1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
            amt1 = amount - price
            if line.discount2:
                price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                price = price - (float(discount2))
            amt2 = amount - amt1 - price
            price *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price = price - (float(discount3))
            amt3 = amount - amt1 - amt2 - price
            return round(amt3 * line.product_uom_qty, 2)
        if disc_no == 4:
            amt1 = amt2 = amt3 = amt4 = 0
            price = line.price_unit
            if line.discount1:
                price = price * (1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
            amt1 = amount - price
            if line.discount2:
                price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                price = price - (float(discount2))
            amt2 = amount - amt1 - price
            if line.discount3:
                price *= (1 - (float(disc_per3) or 0.0) / 100.0)
                price = price - (float(discount3))
            amt3 = amount - amt1 - amt2 - price
            price *= (1 - (float(disc_per4) or 0.0) / 100.0)
            price = price - (float(discount4))
            amt4 = amount - amt3 - amt1 - amt2 - price
            return round(amt4 * line.product_uom_qty, 2)

    def generate_xlsx_report(self, workbook, data, wiz):

        category = []
        group_by_items = []
        grouped_dict = {}
        date_to = str(wiz.date_to) + ' ' + '23:59:59'
        date_from = str(wiz.date_from) + ' ' + '00:00:00'
        if wiz.customer_id:
            customers = wiz.customer_id.ids
        else:
            customers = self.env['res.partner'].search([('customer', '=', True)]).ids
        if wiz.categ_id:
            for parent in wiz.categ_id:
                childes = self.env['product.category'].search([('id', 'child_of', parent.id)])
                for child in childes:
                    category.append(child.id)
        else:
            category = self.env['product.category'].search([]).ids
        domain = [('order_id.confirmation_date', '<=', date_to), ('order_id.confirmation_date', '>=', date_from),
                  ('order_id.partner_id', 'in', customers), ('order_id.state', '=', 'sale'),
                  ('product_id.categ_id', 'in', category)]
        sale_order_lines = self.env['sale.order.line'].search(domain).sorted(key=lambda r: r.order_id.name)
        # print(company_id)
        # [('invoice_number', 'Invoice Number'),
        #  ('sales_person', 'Sales Person'),
        #  ('product', 'Product'),
        #  ('category', 'Category'),
        #  ('customer', 'Customer'),
        #  ('kecamatan', 'Kecamatan')
        if wiz.group_by:
            if wiz.group_by == 'product':
                for grp_line in sale_order_lines:
                    if grp_line.product_id not in group_by_items:
                        group_by_items.append(grp_line.product_id)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.product_id.id == item.id)
                    grouped_dict[item.name] = lines_filtered
            if wiz.group_by == 'category':
                for grp_line in sale_order_lines:
                    if grp_line.categ_id not in group_by_items:
                        group_by_items.append(grp_line.categ_id)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.categ_id.id == item.id)
                    grouped_dict[item.name] = lines_filtered
            if wiz.group_by == 'customer':
                for grp_line in sale_order_lines:
                    if grp_line.order_id.partner_id not in group_by_items:
                        group_by_items.append(grp_line.order_id.partner_id)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.order_id.partner_id == item)
                    grouped_dict[item.name] = lines_filtered
            if wiz.group_by == 'sales_person':
                for grp_line in sale_order_lines:
                    if grp_line.order_id.user_id not in group_by_items:
                        group_by_items.append(grp_line.order_id.user_id)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.order_id.user_id == item)
                    grouped_dict[item.name] = lines_filtered
            if wiz.group_by == 'sale_order':
                for grp_line in sale_order_lines:
                    if grp_line.order_id.name not in group_by_items:
                        group_by_items.append(grp_line.order_id.name)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.order_id.name == item)
                    grouped_dict[item] = lines_filtered
            if wiz.group_by == 'kecamatan':
                for grp_line in sale_order_lines:
                    if grp_line.x_kecamatan not in group_by_items:
                        group_by_items.append(grp_line.x_kecamatan)
                for item in group_by_items:
                    lines_filtered = sale_order_lines.filtered(lambda line: line.x_kecamatan == item)
                    grouped_dict[item] = lines_filtered

        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15,
                                              # 'bg_color': '#0077b3',
                                              })
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11,
                                                  # 'bg_color': '#0077b3',
                                                  # 'font_color': '#FFFFFF'
                                                  })
        sub_heading_format_company = workbook.add_format({'align': 'left',
                                                          'valign': 'left',
                                                          'bold': True, 'size': 11,
                                                          # 'bg_color': '#0077b3',
                                                          # 'font_color': '#FFFFFF'
                                                          })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })
        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })
        line_format = workbook.add_format({'align': 'center',
                                           'valign': 'vcenter',
                                           'size': 1,
                                           'bg_color': '#9A9A9A',
                                           })

        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Laporan Penjualan')
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        worksheet.set_column('O:O', 20)
        worksheet.set_column('P:P', 20)
        worksheet.set_column('Q:Q', 20)
        worksheet.set_column('R:R', 20)
        worksheet.set_column('S:S', 20)
        worksheet.set_column('T:T', 20)
        row = 1
        worksheet.set_row(1, 20)
        starting_col = excel_style(row + 1, 1)
        ending_col = excel_style(row + 1, 17)
        worksheet.merge_range(('A3:B5'), ('A3:B5'), line_format)
        from_date = datetime.datetime.strptime(str(wiz.date_from), '%Y-%m-%d').strftime('%d/%m/%Y')
        to_date = datetime.datetime.strptime(str(wiz.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        date_today = str(fields.Date.today())
        company = self.env.user.company_id
        company_name = ''
        address1 = ''
        address2 = ''
        if company:
            addr1 = []
            addr2 = []
            company_name = company.name
            if company.street:
                addr1.append(company.street)
            if company.street2:
                addr1.append(company.street2)
            if company.city:
                addr1.append(company.city)
            if company.state_id:
                addr1.append(company.state_id.name)
            if company.zip:
                addr2.append(company.zip)

            if company.country_id:
                addr2.append(company.country_id.name)
            address1 = ", ".join(addr1)
            address2 = ", ".join(addr2)

        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              "Store Report" + " " + ':' + " " + from_date + " " + 'TO' + " " + to_date, heading_format)
        starting_cols = excel_style(row, 1)
        ending_cols = excel_style(row, 3)
        worksheet.merge_range('%s:%s' % (starting_cols, ending_cols), '  ', data_format)
        row += 1
        col = 0
        start_address1 = excel_style(row + 2, 4)
        end_address1 = excel_style(row + 2, 5)
        start_address2 = excel_style(row + 3, 4)
        end_address2 = excel_style(row + 3, 5)

        worksheet.write(row, 2, "Company", sub_heading_format_company)
        worksheet.write(row, 3, company_name, sub_heading_format_company)
        worksheet.write(row + 1, 2, "Company Address", sub_heading_format_company)
        worksheet.merge_range('%s:%s' % (start_address1, end_address1), ' ' + address1, sub_heading_format_company)
        worksheet.merge_range('%s:%s' % (start_address2, end_address2), ' ' + address2, sub_heading_format_company)

        row += 4
        worksheet.write(row, 0, "Print Date", sub_heading_format_company)
        worksheet.write(row, 1, date_today, sub_heading_format_company)
        row += 1
        buf_image = io.BytesIO(base64.b64decode(self.env.user.company_id.logo))

        worksheet.insert_image('A3', "any_name.png", {'image_data': buf_image, 'x_scale': 0.215, 'y_scale': 0.15})

        if grouped_dict:
            for grp in grouped_dict:
                sale_order_lines = grouped_dict[grp]
                total_subtotal = 0
                total_disc_qty = 0
                price_tax = 0
                total_price_subtotal = 0
                sl_no = 0
                if sale_order_lines:
                    total_subtotal = sum(line.price_unit * line.product_uom_qty for line in sale_order_lines)
                    total_disc_qty = sum(sale_order_lines.mapped('additional_uom_qty'))
                    price_tax = round(sum(sale_order_lines.mapped('price_tax')), 2)
                    total_price_subtotal = round(sum(sale_order_lines.mapped('price_subtotal')), 2)

                ##FORMATS##

                row += 1

                row_no = row

                if wiz.group_by:
                    row += 1
                row += 1
                headings = ['Sl No', 'Kecamatan', 'Dokumen Sumber', 'Transaction Date', 'Customer Code',
                            'Customer Name', 'Salesman', 'Code',
                            'Product Name', 'Qty', 'UOM', 'Price', 'Subtotal', 'Disc Qty', 'Disc.R', 'Disc.C', 'Disc.T',
                            'Disc.D',
                            'PPN', 'Grand Total']

                if wiz.group_by == 'product':
                    headings.remove('Code')
                    headings.remove('Product Name')
                if wiz.group_by == 'customer':
                    headings = ['Sl No', 'Kecamatan', 'Dokumen Sumber', 'Transaction Date', 'Code',
                                'Product Name',
                                'Salesman', 'Qty', 'UOM', 'Price', 'Subtotal', 'Disc Qty', 'Disc.R', 'Disc.C',
                                'Disc.T', 'Disc.D',
                                'PPN', 'Grand Total']
                if wiz.group_by == 'sale_order':
                    headings.remove('Dokumen Sumber')
                if wiz.group_by == 'kecamatan':
                    headings.remove('Kecamatan')
                if wiz.group_by == 'sales_person':
                    headings.remove('Salesman')
                for heading in headings:
                    worksheet.write(row, headings.index(heading), heading, sub_heading_format)

                row += 1
                disc1_total = disc2_total = disc3_total = disc4_total = 0.00
                for line in sale_order_lines:
                    confirmation_date = False
                    table_data = []
                    default_code = ''
                    customer_code = ''

                    if line.order_id.confirmation_date:
                        confirmation_date = datetime.datetime.strptime(str(line.order_id.confirmation_date.date()),
                                                                       '%Y-%m-%d').strftime('%d-%b-%Y')
                    sl_no += 1
                    table_data.append(sl_no)
                    table_data.append(line.x_kecamatan)
                    table_data.append(line.order_id.name if line.order_id.name else '')
                    table_data.append(confirmation_date if confirmation_date else '')
                    table_data.append(line.order_id.partner_id.ref)
                    customer_code = line.order_id.partner_id.ref
                    table_data.append(line.order_id.partner_id.name)
                    table_data.append(line.order_id.user_id.name if line.order_id.user_id else '')
                    table_data.append(line.product_id.default_code)
                    default_code = line.product_id.default_code
                    table_data.append(line.product_id.name)
                    table_data.append(line.product_uom_qty if line.product_uom_qty else 0)
                    table_data.append(line.product_uom.name if line.product_uom.name else '')
                    table_data.append(line.price_unit if line.price_unit else '')
                    table_data.append(
                        line.price_unit * line.product_uom_qty if line.price_unit * line.product_uom_qty else 0)
                    table_data.append(line.additional_uom_qty if line.additional_uom_qty else 0)
                    table_data.append(line.discount1)
                    table_data.append(line.discount2)
                    table_data.append(line.discount3)
                    table_data.append(line.discount4)
                    table_data.append(",".join(tax.name for tax in line.tax_id))
                    table_data.append(line.price_total)

                    if wiz.group_by == 'product':
                        table_data.remove(line.product_id.default_code)
                        table_data.remove(line.product_id.name)
                    if wiz.group_by == 'customer':
                        table_data = []
                        table_data.append(sl_no)
                        table_data.append(line.x_kecamatan)
                        table_data.append(line.order_id.name if line.order_id.name else '')
                        table_data.append(confirmation_date if confirmation_date else '')
                        table_data.append(line.product_id.default_code)
                        table_data.append(line.product_id.name)
                        customer_code = line.order_id.partner_id.ref
                        table_data.append(line.order_id.user_id.name if line.order_id.user_id else '')
                        default_code = line.product_id.default_code
                        table_data.append(line.product_uom_qty if line.product_uom_qty else 0)
                        table_data.append(line.product_uom.name if line.product_uom.name else '')
                        table_data.append(line.price_unit if line.price_unit else '')
                        table_data.append(
                            line.price_unit * line.product_uom_qty if line.price_unit * line.product_uom_qty else 0)
                        table_data.append(line.additional_uom_qty if line.additional_uom_qty else 0)
                        table_data.append(line.discount1)
                        table_data.append(line.discount2)
                        table_data.append(line.discount3)
                        table_data.append(line.discount4)
                        table_data.append(",".join(tax.name for tax in line.tax_id))
                        table_data.append(line.price_total)
                    if wiz.group_by == 'sale_order':
                        table_data.remove(line.order_id.name)
                    if wiz.group_by == 'kecamatan':
                        table_data.remove(line.x_kecamatan)
                    if wiz.group_by == 'sales_person':
                        table_data.remove(line.order_id.user_id.name if line.order_id.user_id else '')
                    col = 0
                    for data in table_data:
                        worksheet.write(row, col, data, data_format)
                        col += 1

                    disc1_total += self.calculate_discount_amount(line, 1)
                    disc2_total += self.calculate_discount_amount(line, 2)
                    disc3_total += self.calculate_discount_amount(line, 3)
                    disc4_total += self.calculate_discount_amount(line, 4)
                    row += 1
                row += 1
                worksheet.write(row, col-2, 'Subtotal          :', col_format)
                worksheet.write(row, col-1, total_subtotal, data_format)
                worksheet.write(row + 1, col-2, 'Total Disc. Qty :', col_format)
                worksheet.write(row + 1, col-1, total_disc_qty, data_format)
                worksheet.write(row + 2, col-2, 'Total Disc. R    :', col_format)
                worksheet.write(row + 2, col-1, disc1_total, data_format)
                worksheet.write(row + 3, col-2, 'Total Disc. C    :', col_format)
                worksheet.write(row + 3, col-1, disc2_total, data_format)
                worksheet.write(row + 4, col-2, 'Total Disc. T    :', col_format)
                worksheet.write(row + 4, col-1, disc3_total, data_format)
                worksheet.write(row + 5, col-2, 'Total Disc. D    :', col_format)
                worksheet.write(row + 5, col-1, disc4_total, data_format)
                worksheet.write(row + 6, col-2, 'Total DPP        :', col_format)
                worksheet.write(row + 6, col-1, total_price_subtotal, data_format)
                worksheet.write(row + 7, col-2, 'Total PPN        :', col_format)
                worksheet.write(row + 7, col-1, price_tax, data_format)
                worksheet.write(row + 8, col-2, 'Grand Total      :', col_format)
                worksheet.write(row + 8, col-1, round(total_price_subtotal + price_tax, 2), sub_heading_format)
                row += 10

                if wiz.group_by == 'product':
                    if default_code:
                        worksheet.merge_range(row_no, 0, row_no, 4,
                                              "Product : " + grp + ' , ' + 'Code : ' + str(default_code),
                                              sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 4, "Product : " + grp, sub_heading_format_company)

                if wiz.group_by == 'customer':
                    if customer_code:
                        worksheet.merge_range(row_no, 0, row_no, 4,
                                              "Customer : " + grp + ' , ' + 'Customer Code : ' + str(customer_code),
                                              sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 4, "Customer : " + grp, sub_heading_format_company)

                if wiz.group_by == 'category':
                    if grp:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Category : " + grp, sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Category : " + '', sub_heading_format_company)

                if wiz.group_by == 'sales_person':
                    if grp:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Sales Person : " + grp, sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Sales Person : " + ' ', sub_heading_format_company)

                if wiz.group_by == 'sale_order':
                    if grp:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Sales Order : " + grp, sub_heading_format_company)
                        worksheet.write(row, 1, grp, sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Sales Order : " + ' ', sub_heading_format_company)

                if wiz.group_by == 'kecamatan':
                    if grp:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Kecamatan : " + grp, sub_heading_format_company)
                    else:
                        worksheet.merge_range(row_no, 0, row_no, 2, "Kecamatan : " + ' ', sub_heading_format_company)

                starting_cols_line = excel_style(row, 1)
                ending_cols_line = excel_style(row, col)
                worksheet.merge_range('%s:%s' % (starting_cols_line, ending_cols_line), ' ', line_format)
        else:
            total_subtotal = 0
            total_disc_qty = 0
            price_tax = 0
            total_price_subtotal = 0
            sl_no = 0
            if sale_order_lines:
                total_subtotal = sum(line.price_unit * line.product_uom_qty for line in sale_order_lines)
                total_disc_qty = sum(sale_order_lines.mapped('additional_uom_qty'))
                price_tax = round(sum(sale_order_lines.mapped('price_tax')), 2)
                total_price_subtotal = round(sum(sale_order_lines.mapped('price_subtotal')), 2)
            row += 1
            worksheet.write(row, 0, "Sl No", sub_heading_format)
            worksheet.write(row, 1, "Kecamatan", sub_heading_format)
            worksheet.write(row, 2, "Dokumen Sumber", sub_heading_format)
            worksheet.write(row, 3, "Transaction Date", sub_heading_format)
            worksheet.write(row, 4, "Customer Code", sub_heading_format)
            worksheet.write(row, 5, "Customer Name", sub_heading_format)
            worksheet.write(row, 6, "Salesman", sub_heading_format)
            worksheet.write(row, 7, "Code", sub_heading_format)
            worksheet.write(row, 8, "Product Name", sub_heading_format)
            worksheet.write(row, 9, "Qty", sub_heading_format)
            worksheet.write(row, 10, "UOM", sub_heading_format)
            worksheet.write(row, 11, "Price", sub_heading_format)
            worksheet.write(row, 12, "Subtotal", sub_heading_format)
            worksheet.write(row, 13, "Disc Qty", sub_heading_format)
            worksheet.write(row, 14, "Disc.R", sub_heading_format)
            worksheet.write(row, 15, "Disc.C", sub_heading_format)
            worksheet.write(row, 16, "Disc.T", sub_heading_format)
            worksheet.write(row, 17, "Disc.D", sub_heading_format)
            worksheet.write(row, 18, "PPN", sub_heading_format)
            worksheet.write(row, 19, "Grand Total", sub_heading_format)
            row += 1
            disc1_total = disc2_total = disc3_total = disc4_total = 0.00
            for line in sale_order_lines:
                confirmation_date = False
                if line.order_id.confirmation_date:
                    confirmation_date = datetime.datetime.strptime(str(line.order_id.confirmation_date.date()),
                                                                   '%Y-%m-%d').strftime('%d-%b-%Y')
                sl_no += 1
                worksheet.write(row, 0, sl_no, data_format)
                worksheet.write(row, 1, line.x_kecamatan, data_format)
                worksheet.write(row, 2, line.order_id.name, data_format)
                worksheet.write(row, 3, confirmation_date, data_format)
                worksheet.write(row, 4, line.order_id.partner_id.ref, data_format)
                worksheet.write(row, 5, line.order_id.partner_id.name, data_format)
                worksheet.write(row, 6, line.order_id.user_id.name if line.order_id.user_id else '', data_format)
                worksheet.write(row, 7, line.product_id.default_code, data_format)
                worksheet.write(row, 8, line.product_id.name, data_format)
                worksheet.write(row, 9, line.product_uom_qty, data_format)
                worksheet.write(row, 10, line.product_uom.name, data_format)
                worksheet.write(row, 11, line.price_unit, data_format)
                worksheet.write(row, 12, line.price_unit * line.product_uom_qty, data_format)
                worksheet.write(row, 13, line.additional_uom_qty, data_format)
                worksheet.write(row, 14, line.discount1, data_format)
                worksheet.write(row, 15, line.discount2, data_format)
                worksheet.write(row, 16, line.discount3, data_format)
                worksheet.write(row, 17, line.discount4, data_format)
                worksheet.write(row, 18, ",".join(tax.name for tax in line.tax_id), data_format)
                worksheet.write(row, 19, line.price_total, data_format)
                disc1_total += self.calculate_discount_amount(line, 1)
                disc2_total += self.calculate_discount_amount(line, 2)
                disc3_total += self.calculate_discount_amount(line, 3)
                disc4_total += self.calculate_discount_amount(line, 4)
                row += 1
            row += 1
            worksheet.write(row, 18, 'Subtotal          :', col_format)
            worksheet.write(row, 19, total_subtotal, data_format)
            worksheet.write(row + 1, 18, 'Total Disc. Qty :', col_format)
            worksheet.write(row + 1, 19, total_disc_qty, data_format)
            worksheet.write(row + 2, 18, 'Total Disc. R    :', col_format)
            worksheet.write(row + 2, 19, disc1_total, data_format)
            worksheet.write(row + 3, 18, 'Total Disc. C    :', col_format)
            worksheet.write(row + 3, 19, disc2_total, data_format)
            worksheet.write(row + 4, 18, 'Total Disc. T    :', col_format)
            worksheet.write(row + 4, 19, disc3_total, data_format)
            worksheet.write(row + 5, 18, 'Total Disc. D    :', col_format)
            worksheet.write(row + 5, 19, disc4_total, data_format)
            worksheet.write(row + 6, 18, 'Total DPP        :', col_format)
            worksheet.write(row + 6, 19, total_price_subtotal, data_format)
            worksheet.write(row + 7, 18, 'Total PPN        :', col_format)
            worksheet.write(row + 7, 19, price_tax, data_format)
            worksheet.write(row + 8, 18, 'Grand Total      :', col_format)
            worksheet.write(row + 8, 19, round(total_price_subtotal + price_tax, 2), sub_heading_format)
            row += 10
            starting_cols_line = excel_style(row, 1)
            ending_cols_line = excel_style(row, 20)
            worksheet.merge_range('%s:%s' % (starting_cols_line, ending_cols_line), ' ', line_format)
            # worksheet.row_dimensions[row].height = 10
