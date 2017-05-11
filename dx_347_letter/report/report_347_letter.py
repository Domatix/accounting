# -*- coding: utf-8 -*-
###############################################################################
#    Module created by domatix
#    OpenERP, Open Source Management Solution
#
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
from openerp.tools.translate import _
from openerp import models, api
from datetime import datetime
from openerp.exceptions import Warning
import openerp
import base64
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class report_347(models.Model):
    _inherit = "l10n.es.aeat.mod347.partner_record"

    def get_date(self):
        company = self.report_id.company_id.city
        res = company+",   "
        date = datetime.today()
        day = date.strftime("%d")
        month = date.strftime("%B").upper()
        year = date.strftime("%Y")
        res += day + _("  of  ")
        res += month + _("  of  ")
        res += year
        return res

    @api.multi
    def email_letter(self):
        not_sent = []
        blank_email = []
        txt = ''
        for record in self:
            if not record.partner_id.email_count:
                blank_email.append(record.partner_id.name)
            conditions = [('name', '=', 'Carta_347.pdf'),
                          ('partner_id', '=', record.partner_id.id),
                          ('company_id', '=', record.report_id.company_id.id)]
            attachment_id = record.env['ir.attachment'].search(conditions).id
            ir_model_data = record.env['ir.model.data']
            email_tmp_obj = record.pool.get('email.template')
            context = record._context.copy()
            context['base_url'] = record.env[
                'ir.config_parameter'].get_param('web.base.url')
            if attachment_id:
                template_id = ir_model_data.get_object_reference(
                    'dx_347_letter', 'email_letter_347')[1]
                email_tmp_obj.write(record._cr, record._uid, template_id, {
                                    'attachment_ids': [(6, 0,
                                                        [attachment_id])]})
                email_tmp_obj.send_mail(record._cr, record._uid,
                                        template_id, record.id,
                                        force_send=True, context=context)
            else:
                self.generate_letter(record)
                template_id = ir_model_data.get_object_reference(
                    'dx_347_letter', 'email_letter_347')[1]
                attachment_id = record.env[
                    'ir.attachment'].search(conditions).id
                if attachment_id:
                    email_tmp_obj.write(record._cr, record._uid, template_id,
                                        {'attachment_ids': [(6, 0,
                                                            [attachment_id])]})
                    email_tmp_obj.send_mail(record._cr, record._uid,
                                            template_id, record.id,
                                            force_send=True, context=context)
                else:
                    not_sent.append(record.partner_id.name)
        if not_sent:
            txt += _('Could not send the email to the following recipients \
            because they do not have the letter 347 generated: \n')
            for x in not_sent:
                txt += str(x) + '\n'
        if blank_email:
            txt += _('The email could not be sent because the following\
            recipients do not have a financial email in the client form: \n')
            for x in blank_email:
                txt += str(x) + '\n'

        if txt:
            self._cr.commit()
            raise Warning(_(txt))

    def generate_letter(self, record):
        conditions = [('report_type', 'in', ['qweb-pdf', 'qweb-html']),
                      ('report_name', '=', u'dx_347_letter.report_347_letter')]
        report = self.env['ir.actions.report.xml'].search(conditions)[0]
        result, format = openerp.report.render_report(record._cr,
                                                      record._uid,
                                                      [record.id],
                                                      report.report_name,
                                                      {'model': record._name},
                                                      context=record._context)

        result = base64.b64encode(result)
        file_name = "Carta_347.pdf"
        repeated_doc_cond = [('name', '=', file_name),
                             ('partner_id', '=', record.partner_id.id),
                             ('company_id', '=',
                              record.report_id.company_id.id)]
        repeated_docs = self.env['ir.attachment'].search(repeated_doc_cond)
        if repeated_docs:
            repeated_docs.unlink()
        attachment = self.env['ir.attachment']
        attachment.create({'name': file_name,
                           'datas': result,
                           'datas_fname': file_name,
                           'res_model': 'res.partner',
                           'type': 'binary',
                           'partner_id': record.partner_id.id,
                           'company_id': record.report_id.company_id.id
                           })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
