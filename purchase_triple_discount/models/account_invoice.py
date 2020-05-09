# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    global_discount_amount = fields.Float(string='Discount Amount')


    def _prepare_invoice_line_from_po_line(self, line):
        vals = super()._prepare_invoice_line_from_po_line(line)
        vals['discount'] = line.discount1
        vals['discount2'] = line.discount2
        vals['discount3'] = line.discount3
        vals['discount4'] = line.discount4
        vals['form_discount'] = line.form_discount
        return vals

    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        """Return the additional move lines for purchase invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id
        if i_line.product_id and i_line.product_id.valuation == 'real_time' and i_line.product_id.type == 'product':
            # get the fiscal position
            fpos = i_line.invoice_id.fiscal_position_id
            # get the price difference account at the product
            acc = i_line.product_id.property_account_creditor_price_difference
            if not acc:
                # if not found on the product get the price difference account at the category
                acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ
            acc = fpos.map_account(acc).id
            # reference_account_id is the stock input account
            reference_account_id = i_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)[
                'stock_input'].id
            diff_res = []
            # calculate and write down the possible price difference between invoice price and product price
            for line in res:
                if line.get('invl_id', 0) == i_line.id and reference_account_id == line['account_id']:
                    # valuation_price unit is always expressed in invoice currency, so that it can always be computed with the good rate
                    valuation_price_unit = company_currency._convert(
                        i_line.product_id.uom_id._compute_price(i_line.product_id.standard_price, i_line.uom_id),
                        inv.currency_id,
                        company=inv.company_id, date=fields.Date.today(), round=False,
                    )

                    if i_line.product_id.cost_method != 'standard' and i_line.purchase_line_id:
                        po_currency = i_line.purchase_id.currency_id
                        po_company = i_line.purchase_id.company_id
                        # for average/fifo/lifo costing method, fetch real cost price from incomming moves
                        valuation_price_unit = po_currency._convert(
                            i_line.purchase_line_id.product_uom._compute_price(i_line.purchase_line_id.price_unit,
                                                                               i_line.uom_id),
                            inv.currency_id,
                            company=po_company, date=inv.date or inv.date_invoice, round=False,
                        )
                        stock_move_obj = self.env['stock.move']
                        valuation_stock_move = stock_move_obj.search([
                            ('purchase_line_id', '=', i_line.purchase_line_id.id),
                            ('state', '=', 'done'), ('product_qty', '!=', 0.0)
                        ])
                        if self.type == 'in_refund':
                            valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_out())
                        elif self.type == 'in_invoice':
                            valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_in())

                        if valuation_stock_move:
                            valuation_price_unit_total = 0
                            valuation_total_qty = 0
                            for val_stock_move in valuation_stock_move:
                                # In case val_stock_move is a return move, its valuation entries have been made with the
                                # currency rate corresponding to the original stock move
                                valuation_date = val_stock_move.origin_returned_move_id.date or val_stock_move.date
                                valuation_price_unit_total += company_currency._convert(
                                    abs(val_stock_move.price_unit) * val_stock_move.product_qty,
                                    inv.currency_id,
                                    company=inv.company_id, date=valuation_date, round=False,
                                )
                                valuation_total_qty += val_stock_move.product_qty

                            # in Stock Move, price unit is in company_currency
                            valuation_price_unit = valuation_price_unit_total / valuation_total_qty
                            valuation_price_unit = i_line.product_id.uom_id._compute_price(valuation_price_unit,
                                                                                           i_line.uom_id)

                        elif i_line.product_id.cost_method == 'fifo':
                            # In this condition, we have a real price-valuated product which has not yet been received
                            valuation_price_unit = po_currency._convert(
                                i_line.purchase_line_id.price_unit, inv.currency_id,
                                company=po_company, date=inv.date or inv.date_invoice, round=False,
                            )

                    interim_account_price = valuation_price_unit * line['quantity']
                    invoice_cur_prec = inv.currency_id.decimal_places

                    price = price_unit = 0.0
                    discount = discount2 = discount3 = discount4 = 0.00
                    disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0
                    if line['quantity'] > 0:
                        if i_line.discount:
                            if '%' not in str(i_line.discount):
                                discount = float(i_line.discount) / line['quantity']
                            else:
                                disc_str = str(i_line.discount).replace(' ', '')
                                disc_per = (disc_str.split('%')[0])
                        if i_line.discount2:
                            if '%' not in str(i_line.discount2):
                                discount2 = float(i_line.discount2) / line['quantity']
                            else:
                                disc_str2 = str(i_line.discount2).replace(' ', '')
                                disc_per2 = (disc_str2.split('%')[0])
                        if i_line.discount3:
                            if '%' not in str(i_line.discount3):
                                discount3 = float(i_line.discount3) / line['quantity']
                            else:
                                disc_str3 = str(i_line.discount3).replace(' ', '')
                                disc_per3 = (disc_str3.split('%')[0])
                        if i_line.discount4:
                            if '%' not in str(i_line.discount4):
                                discount4 = float(i_line.discount4) / line['quantity']
                            else:
                                disc_str4 = str(i_line.discount4).replace(' ', '')
                                disc_per4 = (disc_str4.split('%')[0])
                        if i_line.form_discount:
                            disc_per5 = i_line.form_discount
                        price = i_line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
                        price = price - (float(discount))
                        price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                        price = price - (float(discount2))
                        price *= (1 - (float(disc_per3) or 0.0) / 100.0)
                        price = price - (float(discount3))
                        price *= (1 - (float(disc_per4) or 0.0) / 100.0)
                        price = price - (float(discount4))
                        price *= (1 - (disc_per5 or 0.0) / 100.0)
                        price_unit = price

                    # price with discount and without tax included
                    # price_unit = i_line.price_unit * (1 - (i_line.discount or 0.0) / 100.0)
                    tax_ids = []
                    if line['tax_ids']:
                        # line['tax_ids'] is like [(4, tax_id, None), (4, tax_id2, None)...]
                        taxes = self.env['account.tax'].browse([x[1] for x in line['tax_ids']])
                        price_unit = taxes.compute_all(price_unit, currency=inv.currency_id, quantity=1.0)[
                            'total_excluded']
                        for tax in taxes:
                            tax_ids.append((4, tax.id, None))
                            for child in tax.children_tax_ids:
                                if child.type_tax_use != 'none':
                                    tax_ids.append((4, child.id, None))

                    if float_compare(valuation_price_unit, price_unit,
                                     precision_digits=invoice_cur_prec) != 0 and float_compare(line['price_unit'],
                                                                                               i_line.price_unit,
                                                                                               precision_digits=invoice_cur_prec) == 0:
                        price_before = line.get('price', 0.0)
                        price_unit_val_dif = price_unit - valuation_price_unit

                        price_val_dif = price_before - interim_account_price
                        if inv.currency_id.compare_amounts(price_unit, valuation_price_unit) != 0 and acc:
                            # If the unit prices have not changed and we have a
                            # valuation difference, it means this difference is due to exchange rates,
                            # so we don't create anything, the exchange rate entries will
                            # be processed automatically by the rest of the code.
                            diff_line = {
                                'type': 'src',
                                'name': i_line.name[:64],
                                'price_unit': price_unit_val_dif,
                                'quantity': line['quantity'],
                                'price': inv.currency_id.round(price_val_dif),
                                'account_id': acc,
                                'product_id': line['product_id'],
                                'uom_id': line['uom_id'],
                                'account_analytic_id': line['account_analytic_id'],
                                'tax_ids': tax_ids,
                            }
                            # We update the original line accordingly
                            # line['price_unit'] doesn't contain the discount, so use price_unit
                            # instead. It could make sense to include the discount in line['price_unit'],
                            # but that doesn't seem a good idea in stable since it is done in
                            # "invoice_line_move_line_get" of "account.invoice".
                            line['price_unit'] = inv.currency_id.round(price_unit - diff_line['price_unit'])
                            line['price'] = inv.currency_id.round(line['price'] - diff_line['price'])
                            diff_res.append(diff_line)
            return diff_res
        return []

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type','global_discount_amount')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.global_discount_amount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                               self.company_id,
                                                               self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                         self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign