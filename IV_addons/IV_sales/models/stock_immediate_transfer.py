# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo import report as odoo_report
import base64


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'


    @api.multi
    def _create_dc_document_line(self, pick_id):
        """
            This function will create auto link document under Document Tab of SO
        """
        sale_obj = self.env['sale.order']
        if pick_id:
            ## Get SO id from current pick_id
            sale_order_id = sale_obj.search([('name','=',pick_id.origin)])

            ## get report template for DC
            template = self.env.ref('IV_reports.report_deliveryslip_inherited', False)
            ## Report Template Name
            report_service = "IV_reports.report_deliveryslip_inherited"
            ## Get report data to print
            result, format = odoo_report.render_report(self._cr, self._uid, [pick_id.id], report_service, {'model': 'stock.picking'}, self._context)
            result = base64.b64encode(result)

            if sale_order_id and result:
                dc_vals = {
                    'document_type': 'Delivery Challan',
                    'document_date': sale_order_id._get_current_date(),#pick_id.min_date,
                    'document_no': pick_id.name,
                    'sale_order_id': sale_order_id.id,
                    'document_filename': pick_id.id,
                    'document_attachment': result,
                }
                ## Create document lines for Delivery Challan
                sale_order_id.document_lines = [[0, 0, dc_vals]]
        return True



    @api.multi
    def process(self):
        """
            Inherit function to create document lines for DC in SO Document Tav
        """
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft':
            self.pick_id.action_confirm()
            if self.pick_id.state != 'assigned':
                self.pick_id.action_assign()
                if self.pick_id.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for pack in self.pick_id.pack_operation_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        self.pick_id.do_transfer()
        ## Call function to create document lines for validate delivery Challan
        self._create_dc_document_line(self.pick_id)
