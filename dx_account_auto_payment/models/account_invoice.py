# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Domatix (http://www.domatix.com)
#                       info <email@domatix.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        autopayments = self.env['account.payment.auto'].search([])
        if not autopayments or not self.payment_mode_id:
            return res
        if self.payment_mode_id.id not in autopayments.payment_ids.ids:
            return res
        else:

            if not self.invoice_line_ids.mapped('sale_line_ids'):
                return res
            date = self.order_date
            if not date:
                date = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')[0].date_order
            payment_method = self.payment_mode_id.payment_method_id
            payment_type = self.payment_mode_id.payment_type
            journal_id = self.payment_mode_id.variable_journal_ids[0]
            payments = self.env['account.payment']
            payment_vals = {'invoice_ids':[(6,0,self.ids)],
                            'amount':self.residual,
                            'payment_date':date,
                            'communication':self.name,
                            'partner_id':self.partner_id.id,
                            'partner_type':self.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
                            'payment_type':payment_type,
                            'journal_id': journal_id.id,
                            'payment_method_id':payment_method.id}

            payment = self.env['account.payment'].create(payment_vals)
            payment.post()
            return res
