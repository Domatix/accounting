# -*- coding: utf-8 -*-
# Copyright 2017 Domatix - Juan Cuesta Contreras
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from itertools import groupby


class iva_record_wizzard(models.TransientModel):
    _name = 'dx_iva_record.iva_record_wizard'

    def get_data(self):
        if self.partner_type == 'supplier':
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('invoice_id.date', '<=', self.date_end), ('tax_id.id', 'in', self.tax_ids.ids), ('company_id', '=', self.company_id.id), ('invoice_id.state', 'in', ['open', 'paid']), ('invoice_id.type', 'in', ['in_invoice', 'in_refund'])])
        elif self.partner_type == 'client':
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('invoice_id.date', '<=', self.date_end), ('tax_id.id', 'in', self.tax_ids.ids), ('company_id', '=', self.company_id.id), ('invoice_id.state', 'in', ['open', 'paid']), ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])])
        else:
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('tax_id.id', 'in', self.tax_ids.ids), ('invoice_id.date', '<=', self.date_end)])

        negative = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed < 0 and 'IGIC' not in r.name)
        positive = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed > 0 and 'IGIC' not in r.name)

        res_dict = {}
        positive = sorted(positive, key=lambda x: x.invoice_id.move_id.date)
        negative = sorted(negative, key=lambda x: x.invoice_id.move_id.date)
        res_dict['positive'] = {}
        res_dict['negative'] = {}

        for key, group in groupby(positive, lambda x: x.name):
            if key not in res_dict['positive']:
                res_dict['positive'][key] = []
            for tax in group:
                res_dict['positive'][key].append(tax)
        for key, group in groupby(negative, lambda x: x.name):
            if key not in res_dict['negative']:
                res_dict['negative'][key] = []
            for tax in group:
                res_dict['negative'][key].append(tax)

        igic_negative = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed < 0 and 'IGIC' in r.name)
        igic_positive = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed > 0 and 'IGIC' in r.name)
        igic_positive = sorted(igic_positive, key=lambda x: x.invoice_id.move_id.date)
        igic_negative = sorted(igic_negative, key=lambda x: x.invoice_id.move_id.date)
        res_dict['igic_positive'] = {}
        res_dict['igic_negative'] = {}
        for key, group in groupby(igic_positive, lambda x: x.name):
            if key not in res_dict['igic_positive']:
                res_dict['igic_positive'][key] = []
            for tax in group:
                res_dict['igic_positive'][key].append(tax)
        for key, group in groupby(igic_negative, lambda x: x.name):
            if key not in res_dict['igic_negative']:
                res_dict['igic_negative'][key] = []
            for tax in group:
                res_dict['igic_negative'][key].append(tax)
        return res_dict.items()

    @api.onchange("partner_type")
    def _onchange_field(self):
        if self.partner_type == 'client':
            self.tax_ids = self.env['account.tax'].search([('type_tax_use',
                                                            '=', 'sale')]).ids
        elif self.partner_type == 'supplier':
            self.tax_ids = self.env['account.tax'].search([('type_tax_use',
                                                            '=',
                                                            'purchase')]).ids

    tax_ids = fields.Many2many(comodel_name='account.tax', string='Taxes')
    company_id = fields.Many2one('res.company', 'Company',
                                 help='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    date_start = fields.Date(
        string='Start date')
    date_end = fields.Date(
        string='End date')

    display_zero = fields.Boolean('Display Zero acc')

    partner_ids = fields.Many2many(comodel_name='res.partner',
                                   string='Partner',
                                   help='Déjelo vacío para todas las empresas')

    partner_type = fields.Selection(
        [('client', 'Cliente'), ('supplier', 'Proveedor')],
        string='Tipo de factura',
        help='Déjelo vacío para todos los tipos de factura')
    igic = fields.Boolean(string="¿Incluir IGIC?")

    def print_report(self, ids, context=None):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dx_iva_record.report_iva_record'
        }
