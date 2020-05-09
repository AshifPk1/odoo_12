from odoo import fields, models, api
from datetime import datetime,date


class StockPicking(models.Model):
    _inherit = "stock.picking"

    vehicle_id = fields.Many2one('fleet.vehicle',string='Vehicle')
    wh_to_driver = fields.Datetime('Journey Start Time')
    driver_to_customer = fields.Datetime('Delivery Execution Time')
    driver_to_warehouse = fields.Datetime('Journey End Time')

    delivery_delay = fields.Char('Delivery Delay',compute='compute_delivery_delay')
    driver_delay = fields.Char('Driver Delay', compute='compute_delivery_delay')
    total_delay = fields.Char('Total Delay', compute='compute_delivery_delay')
    current_date = fields.Date(default=date.today())
    delivery_service = fields.Selection([
        ('0', '0'),
        ('Poor(الأسوء)', 'Poor(الأسوء)'),
        ('Bad(سيئه)', 'Bad(سيئه)'),
        ('Good(جيده)', 'Good(جيده)'),
        ('Very Good(جيده جداَ)', 'Very Good(جيده جداَ)'),
        ('Excellent(ممتازه)', 'Excellent(ممتازه)')], string="Delivery Rating",)
    driver_service = fields.Selection([
        ('0', '0'),
        ('Poor(الأسوء)', 'Poor(الأسوء)'),
        ('Bad(سيئه)', 'Bad(سيئه)'),
        ('Good(جيده)', 'Good(جيده)'),
        ('Very Good(جيده جداَ)', 'Very Good(جيده جداَ)'),
        ('Excellent(ممتازه)', 'Excellent(ممتازه)')],string="Driver Rating",)

    @api.depends('wh_to_driver','driver_to_customer','driver_to_warehouse')
    def compute_delivery_delay(self):
        for rec in self:
            if rec.wh_to_driver and rec.driver_to_customer:
                rec.delivery_delay = rec.driver_to_customer - rec.wh_to_driver
            if rec.driver_to_warehouse and rec.driver_to_customer:
                rec.driver_delay = rec.driver_to_warehouse - rec.driver_to_customer
            if rec.wh_to_driver and rec.driver_to_warehouse:
                rec.total_delay = rec.driver_to_warehouse - rec.wh_to_driver


