# -*- coding: utf-8 -*-


from odoo import models, api, fields, _


class SaleReportStoreWiz(models.TransientModel):
    _name = "sale.report.store.wiz"

    date_from = fields.Date('From')
    date_to = fields.Date('To')
    customer_id = fields.Many2many('res.partner', string='Customer')
    categ_id = fields.Many2many('product.category', string='Product Category')
    group_by = fields.Selection([('sale_order', 'Sale Order'),
                                 ('sales_person', 'Sales Person'),
                                 ('product', 'Product'),
                                 ('category', 'Category'),
                                 ('customer', 'Customer'),
                                 ('kecamatan', 'Kecamatan')
                                 ], string="Group By")

    @api.multi
    def print_report(self):
        data = {'date_from':self.date_from,
                'date_to': self.date_to,
                'customer_id': self.customer_id,
                'categ_id': self.categ_id,
                'wiz_id': self.id}
        return self.env.ref('sale_triple_discount.sales_report_store_action').report_action(self, data=data)

    @api.multi
    def print_report_xlsx(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'customer_id': self.customer_id,
                'categ_id': self.categ_id,
                'group_by': self.group_by,
                'wiz_id': self.id}
        return self.env.ref('sale_triple_discount.store_report_xlsx').report_action(self, data=data)
