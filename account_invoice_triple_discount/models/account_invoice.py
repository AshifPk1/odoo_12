# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    categ_id = fields.Many2one('product.category', string='Product Category', related='invoice_line_ids.categ_id')


    @api.multi
    def _invoice_line_tax_values(self):
        self.ensure_one()
        tax_datas = {}
        TAX = self.env['account.tax']
        for line in self.mapped('invoice_line_ids'):
            discount = discount2 = discount3 = discount4 = 0.00
            disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 =0.0
            if line.discount:
                if '%' not in str(line.discount):
                    discount = float(line.discount)
                else:
                    disc_str = str(line.discount).replace(' ', '')
                    disc_per = (disc_str.split('%')[0])
            if line.discount2:
                if '%' not in str(line.discount2):
                    discount2 = float(line.discount2)
                else:
                    disc_str2 = str(line.discount2).replace(' ', '')
                    disc_per2 = (disc_str2.split('%')[0])
            if line.discount3:
                if '%' not in str(line.discount3):
                    discount3 = float(line.discount3)
                else:
                    disc_str3 = str(line.discount3).replace(' ', '')
                    disc_per3 = (disc_str3.split('%')[0])
            if line.discount4:
                if '%' not in str(line.discount4):
                    discount4 = float(line.discount4)
                else:
                    disc_str4 = str(line.discount4).replace(' ', '')
                    disc_per4 = (disc_str4.split('%')[0])
            if line.form_discount:
                disc_per5 = line.form_discount
            price_unit = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount))
            price_unit *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount2))
            price_unit *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount3))
            price_unit *= (1 - (float(disc_per4) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount4))
            price_unit *= (1 - (disc_per5 or 0.0) / 100.0)
            tax_lines = line.invoice_line_tax_ids.compute_all(price_unit, line.invoice_id.currency_id, line.quantity,
                                                              line.product_id, line.invoice_id.partner_id)['taxes']
            for tax_line in tax_lines:
                tax_line['tag_ids'] = TAX.browse(tax_line['id']).tag_ids.ids
            tax_datas[line.id] = tax_lines
        return tax_datas

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        price_unit = 0.0
        for line in self.invoice_line_ids:
            if not line.account_id:
                continue
            discount = discount2 = discount3 = discount4 = 0.00
            disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0
            if line.quantity > 0:
                if line.discount:
                    if '%' not in str(line.discount):
                        discount = float(line.discount)/line.quantity
                    else:
                        disc_str = str(line.discount).replace(' ', '')
                        disc_per = (disc_str.split('%')[0])
                if line.discount2:
                    if '%' not in str(line.discount2):
                        discount2 = float(line.discount2)/line.quantity
                    else:
                        disc_str2 = str(line.discount2).replace(' ', '')
                        disc_per2 = (disc_str2.split('%')[0])
                if line.discount3:
                    if '%' not in str(line.discount3):
                        discount3 = float(line.discount3)/line.quantity
                    else:
                        disc_str3 = str(line.discount3).replace(' ', '')
                        disc_per3 = (disc_str3.split('%')[0])
                if line.discount4:
                    if '%' not in str(line.discount4):
                        discount4 = float(line.discount4)/line.quantity
                    else:
                        disc_str4 = str(line.discount4).replace(' ', '')
                        disc_per4 = (disc_str4.split('%')[0])
                if line.form_discount:
                    disc_per5 = line.form_discount
                price_unit = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
                price_unit = price_unit - (float(discount))
                price_unit *= (1 - (float(disc_per2) or 0.0) / 100.0)
                price_unit = price_unit - (float(discount2))
                price_unit *= (1 - (float(disc_per3) or 0.0) / 100.0)
                price_unit = price_unit - (float(discount3))
                price_unit *= (1 - (float(disc_per4) or 0.0) / 100.0)
                price_unit = price_unit - (float(discount4))
                price_unit *= (1 - (disc_per5 or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    additional_uom_qty = fields.Float(string='Disc Quantity', default=0)

    discount = fields.Char('Disc R', store=True)
    discount2 = fields.Char('Disc C', store=True)
    discount3 = fields.Char('Disc T', store=True)
    discount4 = fields.Char('Disc D', store=True)
    form_discount = fields.Float('Form Discount', digits=(16, 20))

    sl_no = fields.Integer(string="SL#", compute='_get_sl_no')

    categ_id = fields.Many2one('product.category', string='Product Category', store=True)

    @api.onchange('product_id')
    def onchange_product_id_categ(self):
        self.categ_id = False
        if self.product_id and self.product_id.categ_id:
            self.categ_id = self.product_id.categ_id.id

    @api.depends('invoice_id', 'invoice_id.invoice_line_ids')
    def _get_sl_no(self):
        for record in self:
            count = 0
            if record.invoice_id.invoice_line_ids:
                count = 0
                for lines in record.invoice_id.invoice_line_ids:
                    count += 1
                    lines.update({'sl_no': count})

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        discount = discount2 = discount3 = discount4 = 0.00
        disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 =0.0
        price = 0.0
        if self.quantity > 0:
            if self.discount:
                if '%' not in str(self.discount):
                    discount = float(self.discount)/self.quantity
                else:
                    disc_str = str(self.discount).replace(' ', '')
                    disc_per = (disc_str.split('%')[0])
            if self.discount2:
                if '%' not in str(self.discount2):
                    discount2 = float(self.discount2)/self.quantity
                else:
                    disc_str2 = str(self.discount2).replace(' ', '')
                    disc_per2 = (disc_str2.split('%')[0])
            if self.discount3:
                if '%' not in str(self.discount3):
                    discount3 = float(self.discount3)/self.quantity
                else:
                    disc_str3 = str(self.discount3).replace(' ', '')
                    disc_per3 = (disc_str3.split('%')[0])
            if self.discount4:
                if '%' not in str(self.discount4):
                    discount4 = float(self.discount4)/self.quantity
                else:
                    disc_str4 = str(self.discount4).replace(' ', '')
                    disc_per4 = (disc_str4.split('%')[0])
            if self.form_discount:
                disc_per5 = self.form_discount
            price = self.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price = price - (float(discount))
            price *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price = price - (float(discount2))
            price *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price = price - (float(discount3))
            price *= (1 - (float(disc_per4) or 0.0) / 100.0)
            price = price - (float(discount4))
            price *= (1 - (disc_per5 or 0.0) / 100.0)


        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id,
                                                      self.company_id or self.env.user.company_id,
                                                      date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
