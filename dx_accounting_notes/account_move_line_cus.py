from openerp import models, api


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    # override list in custom module to add/drop columns or change order
    @api.model
    def _report_xls_fields(self):
        return [
            'date', 'period', 'account', 'name', 'debit', 'credit',
            'date_maturity',  'journal',
        ]
