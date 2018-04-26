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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning

class SaleOrderGroup(models.TransientModel):
    _name = 'sale.order.group.channel'
    _description = 'Group Sale orders by channel'

    def _get_partner_by_channel(self):
        if 'active_ids' in self.env.context:
            sale_obj = self.env['sale.order']
            active_ids = self.env.context['active_ids']
            orders = sale_obj.browse(active_ids)
            canales = orders.mapped('channel')
            check = canales[1:] == canales[:-1]
            if not check:
                raise Warning(_("Sale orders with different channels"))
            invoice_status = orders.mapped('invoice_status')
            for status in invoice_status:
                if status != 'to invoice':
                    raise Warning(_("Sale orders must be to invoice and confirmed"))
            res_obj = self.env['res.partner']
            partner_id = res_obj.search([('comercial','=',orders[0].channel)])
            if partner_id:
                partner_id = partner_id[0]
            return partner_id

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        help='Invoice partner',
        default=_get_partner_by_channel)




    @api.multi
    def button_confirm(self):

        if 'active_ids' in self.env.context:
            sale_obj = self.env['sale.order']
            sale_line_obj = self.env['sale.order.line']
            inv_obj = self.env['account.invoice']
            active_ids = self.env.context['active_ids']
            orders = sale_obj.browse(active_ids)
            orders = orders.sorted("name")
            partner_id = self.partner_id
            name = False
            for order_parent in orders:
                if not name:
                    name = order_parent.name
                    origin = order_parent.name
                else:
                    name += ' ' + order_parent.name
                    origin += ' ' + order_parent.name


            invoice_id = inv_obj.create({
                'origin': origin,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id,
                'partner_shipping_id': partner_id.id,
                'merged': True,
                'fiscal_position_id': partner_id.property_account_position_id.id,
                'user_id': orders[0].user_id.id,
            })
            for order in orders.mapped('order_line'):
                ir_property_obj = self.env['ir.property']

                account_id = False
                if order.product_id.id:
                    account_id = order.product_id.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                    account_id = order.order_id.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
                invoice_id.write({

                    'invoice_line_ids': [(0, 0, {
                        'name': order.name,
                        'origin': order.order_id.name,
                        'account_id': account_id,
                        'price_unit': order.price_unit,
                        'quantity': order.product_uom_qty,
                        'discount': 0.0,
                        'uom_id': order.product_id.uom_id.id,
                        'product_id': order.product_id.id,
                        'sale_line_ids': [(6, 0, [order.id])],
                        'invoice_line_tax_ids': [(6, 0, [order.tax_id.id])],
                        'account_analytic_id': order.order_id.project_id.id or False,
                    })],
                })
            invoice_id.compute_taxes()
            return orders.action_view_invoice()
