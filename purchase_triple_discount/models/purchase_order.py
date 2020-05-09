# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    total_discount = fields.Float(string='Discount', compute='compute_total_discount')

    categ_id = fields.Many2one('product.category', string='Product Category', related='order_line.categ_id')

    global_discount_amount = fields.Float(string='Discount Amount', compute='_amount_all')



    @api.depends('order_line.price_subtotal', 'order_line')
    def compute_total_discount(self):
        for rec in self:
            for order in rec:
                amount_discount = 0.0
                for line in order.order_line:
                    amount_discount += ((line.product_qty * line.price_unit)-line.price_subtotal)
                order.update({
                    'total_discount': order.currency_id.round(amount_discount),
                })

    # @api.onchange('discount_type', 'discount_rate', 'order_line')
    # def supply_rate(self):
    #     for order in self:
    #         if order.discount_rate:
    #             if order.discount_type == 'percent':
    #                 for line in order.order_line:
    #                     line.form_discount = order.discount_rate
    #             else:
    #                 total = discount = 0.0
    #                 for line in order.order_line:
    #                     price = 0.0
    #                     discount = discount2 = discount3 = discount4 = 0.00
    #                     disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0
    #                     if line.product_uom_qty > 0:
    #                         if line.discount1:
    #                             if '%' not in str(line.discount1):
    #                                 discount = float(line.discount1) / line.product_uom_qty
    #                             else:
    #                                 disc_str = str(line.discount1).replace(' ', '')
    #                                 disc_per = (disc_str.split('%')[0])
    #                         if line.discount2:
    #                             if '%' not in str(line.discount2):
    #                                 discount2 = float(line.discount2) / line.product_uom_qty
    #                             else:
    #                                 disc_str2 = str(line.discount2).replace(' ', '')
    #                                 disc_per2 = (disc_str2.split('%')[0])
    #                         if line.discount3:
    #                             if '%' not in str(line.discount3):
    #                                 discount3 = float(line.discount3) / line.product_uom_qty
    #                             else:
    #                                 disc_str3 = str(line.discount3).replace(' ', '')
    #                                 disc_per3 = (disc_str3.split('%')[0])
    #                         if line.discount4:
    #                             if '%' not in str(line.discount4):
    #                                 discount4 = float(line.discount4) / line.product_uom_qty
    #                             else:
    #                                 disc_str4 = str(line.discount4).replace(' ', '')
    #                                 disc_per4 = (disc_str4.split('%')[0])
    #                         price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
    #                         price = price - (float(discount))
    #                         price *= (1 - (float(disc_per2) or 0.0) / 100.0)
    #                         price = price - (float(discount2))
    #                         price *= (1 - (float(disc_per3) or 0.0) / 100.0)
    #                         price = price - (float(discount3))
    #                         price *= (1 - (float(disc_per4) or 0.0) / 100.0)
    #                         price = price - (float(discount4))
    #                     total += (line.product_uom_qty * price)
    #                     # total += (line.product_qty * line.price_unit)
    #                 if total:
    #                     if order.discount_rate != 0:
    #                         discount = (order.discount_rate / total) * 100
    #                     else:
    #                         discount = order.discount_rate
    #                     for line in order.order_line:
    #                         line.form_discount = discount
    #         else:
    #             for line in order.order_line:
    #                 line.form_discount = 0.00

    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        result['context'].update({
                'default_global_discount_amount': self.global_discount_amount,
                # 'amount_total': self.amount_total,
            })
        print(result['context'],'result')
        return result
    @api.depends('order_line.price_total','discount_type', 'discount_rate')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        super(PurchaseOrder, self)._amount_all()

        for order in self:
            amount_untaxed = amount_tax = 0.0
            total = 0.0
            discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            total = amount_untaxed + amount_tax
            if order.discount_rate:
                if order.discount_type == 'percent':
                    discount = (total * order.discount_rate) / 100
                else:
                    discount = order.discount_rate
            total = total - discount
            print(total,'total')

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': total,
                'global_discount_amount': discount
            })


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sl_no = fields.Integer(string="SL#", compute='_get_sl_no')
    additional_uom_qty = fields.Float(string='Disc Quantity', default=0.0)
    categ_id = fields.Many2one('product.category', string='Product Category', store=True)

    @api.onchange('product_id')
    def onchange_product_id_categ(self):
        self.categ_id = False
        if self.product_id and self.product_id.categ_id:
            self.categ_id = self.product_id.categ_id.id


    @api.depends('order_id', 'order_id.order_line')
    def _get_sl_no(self):
        for record in self:
            count = 0
            if record.order_id.order_line:
                count = 0
                for lines in record.order_id.order_line:
                    count += 1
                    lines.update({'sl_no': count})

    @api.depends('discount1', 'discount2', 'discount3', 'discount4', 'form_discount')
    def _compute_amount(self):
        return super()._compute_amount()

    def _prepare_compute_all_values(self):
        vals = super()._prepare_compute_all_values()
        vals.update({'price_unit': self._get_discounted_price_unit()})
        return vals

    discount1 = fields.Char('Margin')
    discount2 = fields.Char('Cash')
    discount3 = fields.Char('Rp')
    discount4 = fields.Char('Disc.4')
    form_discount = fields.Float('Form Discount', digits=(16, 20))

    # _sql_constraints = [
    #     ('discount2_limit', 'CHECK (discount2 <= 100.0)',
    #      'Discount 2 must be lower than 100%.'),
    #     ('discount3_limit', 'CHECK (discount3 <= 100.0)',
    #      'Discount 3 must be lower than 100%.'),
    # ]

    def _get_discounted_price_unit(self):
        discount = discount2 = discount3 = discount4 = 0.00
        disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0
        price_unit = 0
        if self.product_uom_qty > 0:
            if self.discount1:
                if '%' not in str(self.discount1):
                    discount = float(self.discount1) / self.product_uom_qty
                else:
                    disc_str = str(self.discount1).replace(' ', '')
                    disc_per = (disc_str.split('%')[0])
            if self.discount2:
                if '%' not in str(self.discount2):
                    discount2 = float(self.discount2) / self.product_uom_qty
                else:
                    disc_str2 = str(self.discount2).replace(' ', '')
                    disc_per2 = (disc_str2.split('%')[0])
            if self.discount3:
                if '%' not in str(self.discount3):
                    discount3 = float(self.discount3) / self.product_uom_qty
                else:
                    disc_str3 = str(self.discount3).replace(' ', '')
                    disc_per3 = (disc_str3.split('%')[0])
            if self.discount4:
                if '%' not in str(self.discount4):
                    discount4 = float(self.discount4) / self.product_uom_qty
                else:
                    disc_str4 = str(self.discount4).replace(' ', '')
                    disc_per4 = (disc_str4.split('%')[0])
            if self.form_discount:
                    disc_per5 = self.form_discount
            price_unit = self.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount))
            price_unit *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount2))
            price_unit *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount3))
            price_unit *= (1 - (float(disc_per4) or 0.0) / 100.0)
            price_unit = price_unit - (float(discount4))
            price_unit *= (1 - (disc_per5 or 0.0) / 100.0)
        return price_unit

    @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        order = line.order_id
        price_unit = line._get_discounted_price_unit()
        if line.taxes_id:
            price_unit = line.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=line.order_id.currency_id, quantity=1.0, product=line.product_id,
                partner=line.order_id.partner_id
            )['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id._convert(
                price_unit, order.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(),
                round=False)
        return price_unit

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty + self.additional_uom_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            # Always call '_compute_quantity' to round the diff_quantity. Indeed, the PO quantity
            # is not rounded automatically following the UoM.
            if get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = self.product_uom._compute_quantity(diff_quantity, self.product_uom, rounding_method='HALF-UP')
            res.append(template)
        return res
