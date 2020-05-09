
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'),('female', 'Female')], string='Gender')
