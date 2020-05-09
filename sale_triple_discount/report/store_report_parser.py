# -*- coding: utf-8 -*-

from odoo import api, models


class SaleStoreReport(models.AbstractModel):
    _name = 'report.sale_triple_discount.sales_report_store_template'

    def calculate_discount_amount(self, line, disc_no):
        price = 0.0
        amount = 0.0
        discount = discount2 = discount3 = discount4 = 0.00
        disc_per = disc_per2 = disc_per3 = disc_per4 = 0.0
        amount = line.price_unit
        if line.discount1:
            if '%' not in str(line.discount1):
                discount = float(line.discount1)/line.product_uom_qty
            else:
                disc_str = str(line.discount1).replace(' ', '')
                disc_per = (disc_str.split('%')[0])
        if line.discount2:
            if '%' not in str(line.discount2):
                discount2 = float(line.discount2)/line.product_uom_qty
            else:
                disc_str2 = str(line.discount2).replace(' ', '')
                disc_per2 = (disc_str2.split('%')[0])
        if line.discount3:
            if '%' not in str(line.discount3):
                discount3 = float(line.discount3)/line.product_uom_qty
            else:
                disc_str3 = str(line.discount3).replace(' ', '')
                disc_per3 = (disc_str3.split('%')[0])
        if line.discount4:
            if '%' not in str(line.discount4):
                discount4 = float(line.discount4)/line.product_uom_qty
            else:
                disc_str4 = str(line.discount4).replace(' ', '')
                disc_per4 = (disc_str4.split('%')[0])

        if disc_no == 1:
            price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price = price - (float(discount))
            return round((amount - price)*line.product_uom_qty, 2)
        if disc_no == 2:
            amt1 = amt2 = 0
            price = line.price_unit
            if line.discount1:
                price = price*(1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
            amt1 = amount - price
            price *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price = price - (float(discount2))
            amt2 = amount-amt1-price
            return round(amt2*line.product_uom_qty, 2)
        if disc_no == 3:
            amt1 = amt2 = amt3 = 0
            price = line.price_unit
            if line.discount1:
                price = price*(1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
            amt1 = amount - price
            if line.discount2:
                price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                price = price - (float(discount2))
            amt2 = amount - amt1 - price
            price *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price = price - (float(discount3))
            amt3 = amount-amt1-amt2-price
            return round(amt3*line.product_uom_qty, 2)
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
            return round(amt4*line.product_uom_qty, 2)

    # '23:59:59'
    @api.model
    def _get_report_values(self, docids, data=None):
        category = []
        wiz = self.env['sale.report.store.wiz'].browse(data.get('wiz_id'))
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
        total_subtotal = 0
        total_disc_qty = 0
        price_tax = 0
        total_price_subtotal = 0
        if sale_order_lines:
            total_subtotal = sum(line.price_unit * line.product_uom_qty for line in sale_order_lines)
            total_disc_qty = sum(sale_order_lines.mapped('additional_uom_qty'))
            price_tax = round(sum(sale_order_lines.mapped('price_tax')), 2)
            total_price_subtotal = round(sum(sale_order_lines.mapped('price_subtotal')), 2)

        data = {
            'date_to': wiz.date_to,
            'date_from': wiz.date_from,
            'total_subtotal': total_subtotal,
            'total_price_subtotal': total_price_subtotal,
            'total_disc_qty': total_disc_qty,
            'doc_ids': self.ids,
            'price_tax': price_tax,
            'sale_order_lines': sale_order_lines,
            'disc_amount': self.calculate_discount_amount
        }
        return data
