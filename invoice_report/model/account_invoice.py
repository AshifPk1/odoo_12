from odoo import api, fields, models
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def amount_to_words(self, amount_total):
        return num2words(amount_total, lang='id')
