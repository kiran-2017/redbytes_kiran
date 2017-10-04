# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from num2words import num2words
import datetime
from odoo.exceptions import UserError, ValidationError

from odoo import report as odoo_report
import base64

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    """ Inherit this call for adding new fields on TAX INVOICE"""



    @api.multi
    def _create_invoice_document_line(self):
        """
            This function will create auto link document under Document Tab of SO
        """
        sale_obj = self.env['sale.order']
        if self.origin:
            ## Get SO id from current Invoice id
            sale_order_id = sale_obj.search([('name','=',self.origin)])

            ## get report template for Invoice
            template = self.env.ref('IV_accounting.report_tax_invoice', False)
            ## Report Template Name
            report_service = "IV_accounting.report_tax_invoice"
            ## Get report data to print Invoice report
            result, format = odoo_report.render_report(self._cr, self._uid, [self.id], report_service, {'model': 'account.invoice'}, self._context)
            ## Convert file to binary format
            result = base64.b64encode(result)

            if sale_order_id and result:
                invoice_vals = {
                    'document_type': 'Invoice',
                    'document_date': sale_order_id._get_current_date(),#pick_id.min_date,
                    'document_no': self.number,
                    'sale_order_id': sale_order_id.id,
                    'document_filename': self.id,
                    'document_attachment': result,
                }
                ## Create document lines for Tax Invoice
                sale_order_id.document_lines = [[0, 0, invoice_vals]]
        return True



    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        ## Create Invoice attachment lines on SO Document lines
        self._create_invoice_document_line()
        return to_open_invoices.invoice_validate()
