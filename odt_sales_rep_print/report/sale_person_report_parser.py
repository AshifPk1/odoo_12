from odoo import api, models, fields


class SalePersonReport(models.AbstractModel):
    _name = 'report.odt_sales_rep_print.sale_person_report_pdf_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']. \
            _get_report_from_name('odt_sales_rep_print.sale_person_report_pdf_template')
        from_date = str(data['from_date']) + ' ' + '00:00:00'
        to_date = str(data['to_date']) + ' ' + '23:23:59'
        if data['from_date'] and data['to_date']:
            sale_orders = self.env['sale.order'].search([('confirmation_date', '>=', from_date),
                                                         ('confirmation_date', '<=', to_date),
                                                         ('state', '=', 'sale')])
        op = []

        product_type = {'consu': 'Consumable', 'service': 'Service', 'product': 'Storable Product'}

        for sale_order in sale_orders:
            for line in sale_order.order_line:
                res = dict(
                    (fn, 0.0) for fn in
                    ['salesman', 'location', 'clients', 'years', 'quarter', 'month', 'date', 'code',
                     'product_name', 'product_segmentation', 'quantity', 'price_without_tax', 'price_with_tax', 'gross_margin'])
                gross_total = line.price_subtotal - (line.product_uom_qty * line.product_id.standard_price)
                date = fields.Datetime.from_string(line.order_id.confirmation_date)
                if date.month >= 1 and date.month <= 3:
                    quarter = 'Q1'
                elif date.month >= 4 and date.month <= 6:
                    quarter = 'Q2'
                elif date.month >= 7 and date.month <= 9:
                    quarter = 'Q3'
                else:
                    quarter = 'Q4'

                res['salesman'] = line.order_id.user_id.name
                res['location'] = sale_order.team_id.name
                res['clients'] = line.order_id.partner_id.name
                res['years'] = date.year
                res['quarter'] = quarter
                res['month'] = date.month
                res['date'] = date.day
                res['code'] = line.product_id.default_code
                res['product_name'] = line.product_id.name
                res['product_segmentation'] = product_type[line.product_id.type]
                res['quantity'] = line.product_uom_qty
                res['price_without_tax'] = round(line.price_subtotal,2)
                res['price_with_tax'] = round(line.price_total,2)
                res['gross_margin'] = round(gross_total,2)
                op.append(res)
        data = op
        return {
                'doc_model': report.model,
                'data': data,
                }

    # @api.model
    # def render_html(self, docids, data=None):
    #     print(docids,'inside function')
    #     report_obj = self.env['report']
    #     report = report_obj._get_report_from_name('odt_sales_rep_print.sale_person_report_pdf')
    #     sale_orders = self.env['sale.order'].search()
    #     print(sale_orders,'sale order')
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': report.model,
    #         'docs': sale_orders,
    #     }
    #     return report_obj.render('odt_sales_rep_print.sale_person_report_pdf', docargs)

    # from_date = str(wiz.from_date) + ' ' + '00:00:00'
    # to_date = str(wiz.to_date) + ' ' + '23:23:59'
    # if wiz.from_date and wiz.to_date:
    #     sale_orders = self.env['sale.order'].search([('confirmation_date', '>=', from_date),
    #                                                  ('confirmation_date', '<=', to_date),
    #                                                  ('state', '=', 'sale')])
    # product_type = {'consu': 'Consumable', 'service': 'Service', 'product': 'Storable Product'}
    # for sale_order in sale_orders:
    #     for line in sale_order.order_line:
    #         gross_total = line.price_subtotal - (line.product_uom_qty * line.product_id.standard_price)
    #         date = fields.Datetime.from_string(line.order_id.confirmation_date)
    #         if date.month >= 1 and date.month <= 3:
    #             quarter = 'Q1'
    #         elif date.month >= 4 and date.month <= 6:
    #             quarter = 'Q2'
    #         elif date.month >= 7 and date.month <= 9:
    #             quarter = 'Q3'
    #         else:
    #             quarter = 'Q4'