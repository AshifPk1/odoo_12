# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    additional_uom_qty = fields.Float(string='Disc Quantity', default=0.0)

    sl_no = fields.Integer(string="SL#", compute='_get_sl_no')

    categ_id = fields.Many2one('product.category', string='Product Category', store=True)

    x_kecamatan = fields.Char(string='Kecamatan', store=True)

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

    @api.depends('discount1', 'discount2', 'discount3', 'discount4', 'discounting_type', 'product_uom_qty',
                 'discount', 'price_unit', 'tax_id', 'form_discount')
    def _compute_amount(self):
        # prev_values = self.triple_discount_preprocess()
        # super(SaleOrderLine, self)._compute_amount()
        # self.triple_discount_postprocess(prev_values)
        for line in self:
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
                if line.form_discount:
                    disc_per5 = line.form_discount
                price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
                price = price - (float(discount))
                price *= (1 - (float(disc_per2) or 0.0) / 100.0)
                price = price - (float(discount2))
                price *= (1 - (float(disc_per3) or 0.0) / 100.0)
                price = price - (float(discount3))
                price *= (1 - (float(disc_per4) or 0.0) / 100.0)
                price = price - (float(discount4))
                price *= (1 - (disc_per5 or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    discount1 = fields.Char('Disc R', store=True)
    discount2 = fields.Char('Disc C', store=True)
    discount3 = fields.Char('Disc T', store=True)
    discount4 = fields.Char('Disc D', store=True)
    form_discount = fields.Float('Form Discount', digits=(16, 20))

    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[
            ('additive', 'Additive'),
            ('multiplicative', 'Multiplicative'),
        ],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
             "or multiplicative.\nAdditive discounts are summed first and "
             "then applied.\nMultiplicative discounts are applied sequentially.\n"
             "if apply both multiplicative and additive which will automatically select additive type\n"
             "Multiplicative discounts are default",
    )

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'additional_uom_qty': self.additional_uom_qty,
            'discount': self.discount1,
            'discount2': self.discount2,
            'discount3': self.discount3,
            'discount4': self.discount4,
            'form_discount': self.form_discount
        })
        return res

    @api.depends('price_unit', 'discount', 'discount1', 'discount2', 'discount3', 'discount4', 'form_discount')
    def _get_price_reduce(self):
        price = 0.0
        discount = discount2 = discount3 = discount4 = 0.00
        disc_per = disc_per2 = disc_per3 = disc_per4 = disc_per5 = 0.0

        for line in self:
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
            if line.form_discount:
                disc_str5 = line.form_discount
            price = line.price_unit * (1 - (float(disc_per) or 0.0) / 100.0)
            price = price - (float(discount))
            price *= (1 - (float(disc_per2) or 0.0) / 100.0)
            price = price - (float(discount2))
            price *= (1 - (float(disc_per3) or 0.0) / 100.0)
            price = price - (float(discount3))
            price *= (1 - (float(disc_per4) or 0.0) / 100.0)
            price = price - (float(discount4))
            price *= (1 - (disc_per5 or 0.0) / 100.0)
            line.price_reduce = price

    @api.multi
    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = (line.product_uom_qty + line.additional_uom_qty) - qty
            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer, line.name,
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True
