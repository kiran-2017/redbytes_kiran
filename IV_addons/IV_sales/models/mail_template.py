# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel
import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging
import lxml
import urlparse

from urllib import urlencode, quote as quote

from odoo import _, api, fields, models, tools
from odoo import report as odoo_report
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class MailTemplate(models.Model):
    "Templates for sending email"
    _inherit = "mail.template"


    @api.multi
    def generate_email(self, res_ids, fields=None):
        """Generates an email from the template for given the given model based on
        records given by res_ids.

        :param template_id: id of the template to render.
        :param res_id: id of the record to use for rendering the template (model
                       is taken from template definition)
        :returns: a dict containing all relevant fields for creating a new
                  mail.mail entry, with one extra key ``attachments``, in the
                  format [(report_name, data)] where data is base64 encoded.
        """
        attachment_obj = self.env['ir.attachment']
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, (int, long)):
            res_ids = [res_ids]
            multi_mode = False
        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date']

        res_ids_to_templates = self.get_email_template(res_ids)
        print res_ids_to_templates,'---------res_ids_to_templates'

        # templates: res_id -> template; template -> res_ids
        templates_to_res_ids = {}
        for res_id, template in res_ids_to_templates.iteritems():
            templates_to_res_ids.setdefault(template, []).append(res_id)
        print templates_to_res_ids,'-------templates_to_res_ids'
        results = dict()
        for template, template_res_ids in templates_to_res_ids.iteritems():
            Template = self.env['mail.template']
            # generate fields value for all res_ids linked to the current template
            if template.lang:
                Template = Template.with_context(lang=template._context.get('lang'))
            for field in fields:
                Template = Template.with_context(safe=field in {'subject'})
                generated_field_values = Template.render_template(
                    getattr(template, field), template.model, template_res_ids,
                    post_process=(field == 'body_html'))
                for res_id, field_value in generated_field_values.iteritems():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in fields for field in ['email_to', 'partner_to', 'email_cc']):
                results = template.generate_recipients(results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                # body: add user signature, sanitize
                if 'body_html' in fields and template.user_signature:
                    signature = self.env.user.signature
                    if signature:
                        values['body_html'] = tools.append_content_to_html(values['body_html'], signature, plaintext=False)
                if values.get('body_html'):
                    values['body'] = tools.html_sanitize(values['body_html'])
                # technical settings
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )
            print template, template.report_template,'------template.report_template'
            # Add report in attachments: generate once for all template_res_ids
            if template.report_template:
                if template.report_template.name == 'GAD':
                    attachments = []
                    so_id = self.env['sale.order'].browse(res_id)
                    print so_id,'------so_id'
                    if so_id:
                        attachment_id = attachment_obj.search(([('res_model','=','sale.order'),('res_id','=',so_id.id),('res_name','=',so_id.name),('so_doc_type','=','Approved GA Drawing')]),limit=1)
                        print attachment_id,'-------attachment_ids'
                        if attachment_id:
                            report_name = attachment_id.name
                            result = attachment_id.datas
                            # jfkjdkkkkkk
                            attachments.append((report_name, result))
                            results[res_id]['attachments'] = attachments
                elif template.report_template.name == 'QAP':
                    attachments = []
                    so_id = self.env['sale.order'].browse(res_id)
                    print so_id,'------so_id'
                    if so_id:
                        attachment_id = attachment_obj.search(([('res_model','=','sale.order'),('res_id','=',so_id.id),('res_name','=',so_id.name),('so_doc_type','=','Approved QA Plan')]),limit=1)
                        print attachment_id,'-------attachment_ids'
                        if attachment_id:
                            report_name = attachment_id.name
                            result = attachment_id.datas
                            attachments.append((report_name, result))
                            results[res_id]['attachments'] = attachments
                elif template.report_template.name == 'TPI':
                    attachments = []
                    so_id = self.env['sale.order'].browse(res_id)
                    print so_id,'------so_id'
                    if so_id:
                        attachment_id = attachment_obj.search(([('res_model','=','sale.order'),('res_id','=',so_id.id),('res_name','=',so_id.name),('so_doc_type','=','TPI Call')]),limit=1)
                        print attachment_id,'-------attachment_ids'
                        if attachment_id:
                            report_name = attachment_id.name
                            result = attachment_id.datas
                            attachments.append((report_name, result))
                            results[res_id]['attachments'] = attachments

                else:
                    for res_id in template_res_ids:
                        attachments = []
                        report_name = self.render_template(template.report_name, template.model, res_id)
                        report = template.report_template
                        report_service = report.report_name
                        print report_service, res_id,'--------report_service,res_id'

                        if report.report_type in ['qweb-html', 'qweb-pdf']:
                            result, format = Template.env['report'].get_pdf([res_id], report_service), 'pdf'
                            # print result, format,'---------result, format'
                            # jkjkkkkkk
                        else:
                            result, format = odoo_report.render_report(self._cr, self._uid, [res_id], report_service, {'model': template.model}, Template._context)

                        # TODO in trunk, change return format to binary to match message_post expected format
                        result = base64.b64encode(result)
                        # print result,'--------result'
                        # jfkdsjkkk
                        if not report_name:
                            report_name = 'report.' + report_service
                        ext = "." + format
                        if not report_name.endswith(ext):
                            report_name += ext
                        attachments.append((report_name, result))
                        results[res_id]['attachments'] = attachments

        return multi_mode and results or results[res_ids[0]]



    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.

           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :param dict email_values: if set, the generated mail.message is
                updated with given values dict
           :returns: id of the mail.message that was created
        """
        self.ensure_one()
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id)
        self.generate_email_for_gad(res_id)
        values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
        values.update(email_values or {})
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        # add a protection against void email_from
        if 'email_from' in values and not values.get('email_from'):
            values.pop('email_from')
        mail = Mail.create(values)

        print attachments,'---------attachments'
        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            attachment_ids.append(Attachment.create(attachment_data).id)
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail.write({'attachment_ids': [(6, 0, attachment_ids)]})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?
