# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    categ_id = fields.Many2one('product.category', string='Product Category', related='order_line.categ_id')

    x_kecamatan = fields.Char(string='Kecamatan', related='partner_id.x_kecamatan', store=True)

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_rate:
                if order.discount_type == 'percent':
                    for line in order.order_line:
                        line.form_discount = order.discount_rate
                else:
                    total = discount = 0.0
                    for line in order.order_line:
                        price = 0.0
                        discount = discount2 = discount3 = discount4 = 0.00
                        disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0
                        if line.product_uom_qty > 0:
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
                            price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
                            price = price - (float(discount))
                            price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                            price = price - (float(discount2))
                            price *= (1 - (float(disc_per3) or 0.0) / 100.0)
                            price = price - (float(discount3))
                            price *= (1 - (float(disc_per4) or 0.0) / 100.0)
                            price = price - (float(discount4))
                        total += (line.product_uom_qty * price)
                        # total += (line.product_uom_qty * line.price_unit)
                    if total:
                        if order.discount_rate != 0:
                            discount = (order.discount_rate / total) * 100
                        else:
                            discount = order.discount_rate
                        for line in order.order_line:
                            line.form_discount = discount
            else:
                for line in order.order_line:
                    line.form_discount = 0.00

    @api.multi
    def _get_tax_amount_by_group(self):
        # Copy/paste from standard method in sale
        self.ensure_one()
        res = {}
        for line in self.order_line:
            price_reduce = line.price_reduce  # changed
            taxes = line.tax_id.compute_all(
                price_reduce, quantity=line.product_uom_qty,
                product=line.product_id,
                partner=self.partner_shipping_id)['taxes']
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, 0.0)
                for t in taxes:
                    if (t['id'] == tax.id or
                            t['id'] in tax.children_tax_ids.ids):
                        res[group] += t['amount']
        res = sorted(list(res.items()), key=lambda l: l[0].sequence)
        res = [(l[0].name, l[1]) for l in res]
        return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, final=final
        )
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for inv in invoices:
            inv._onchange_invoice_line_ids()
        return invoice_ids
