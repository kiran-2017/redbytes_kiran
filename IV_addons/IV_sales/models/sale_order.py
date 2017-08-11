# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"
    """ Inherit class for adding new fields on sale order"""


    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        return res

    ## Add data fields here
    ## Inherit states to add more states to SO form
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('Advance Received', 'Advance Received'),
        ('GAD Approved', 'GAD Approved'),
        ('QAP Approved', 'QAP Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    delivery_date = fields.Date(string="Delivery Date")
    is_gad = fields.Selection([('Y', 'Y'), ('N', 'N'), ('NA', 'NA')],string="GAD", help="Will show the value of this field (Whether GA Drawing approved or not)", default='N')
    is_adv = fields.Selection([('Y', 'Y'), ('N', 'N'), ('NA', 'NA')], string="Advance", help="Will show the value of this field (Whether advance received or not)", default='N')
    iv_project_id = fields.Many2one("project.project", string="Project")
    ## Add VALVE LIST values here
    inspection = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Inspection', default='NO')
    agency_name = fields.Char(string="Agency Name")
    painting = fields.Char(string="Painting")
    flange_drilling = fields.Char(string="Flange Drilling")
    packing = fields.Char(string="Packing")
    material_standard = fields.Selection([('IS', 'IS'), ('DIN', 'DIN')], 'Material Standard', default='')
    special_mfg_instruction = fields.Char(string="Special Mfg Instruction")
    ## Add COMMERCIAL group fields here
    advance_bg_required = fields.Selection([('BLANK', '[BLANK]'), ('YES', 'YES'), ('NO', 'NO')], 'Advance BG Required', default='BLANK')
    advance_bg_details = fields.Text(string="Advance BG details")
    warranty = fields.Integer(string="Warranty(Months)", default="12")
    ## Add Delivery group fields
    delivery = fields.Selection([('BLANK', '[BLANK]'), ('Door Delivery', 'Door Delivery'), ('Godown Delivery', 'Godown Delivery')], 'Delivery', default='BLANK')
    freight = fields.Selection([('BLANK', '[BLANK]'), ('To Pay', 'To Pay'), ('Paid', 'Paid')], 'Freight', default='BLANK')
    insurance = fields.Selection([('BLANK', '[BLANK]'), ('NA', 'NA'), ('Our Account', 'Our Account'), ('Client Account', 'Client Account')], 'Insurance', default='BLANK')
    transporter = fields.Char(string="Transporter")
    performance_guarantee = fields.Selection([('BLANK', '[BLANK]'), ('Performance BG', 'Performance BG'), ('Corporate Bond', 'Corporate Bond')], 'Performance Guarantee', default='BLANK')
    delivery_instructions = fields.Text(string="Delivery Instructions")
    # shipping_policy = fields.Char(string="Shipping Policy", default="Deliver each product when available")

    document_lines = fields.One2many('document.lines', 'sale_order_id', string="Documents")

    ## ORDER STATUS fields
    rfq_received_date = fields.Date(string="Date", copy=False)
    rfq_received_by = fields.Char(string="By", copy=False)

    # quotation_sent = fields.Selection([('Y','Y'),('N','N')], string="Quotation Sent", default='N')
    quotation_sent_line_ids = fields.One2many('quotation.sent.line', 'sale_order_id', string="Quotation Sent")
    customer_po_received_line_ids = fields.One2many('customer.po.received.line', 'sale_order_id', string="Quotation Sent")




    order_accepted = fields.Selection([('Y','Y'),('N','N')], string="Order Accepted", default='N')
    order_accepted_date = fields.Date(string="Date")
    order_accepted_by = fields.Char(string="By")

    advance_received = fields.Selection([('Y','Y'),('N','N'),('NA','NA')], string="Advance Received", default='N')
    advance_received_date = fields.Date(string="Date")
    advance_received_by = fields.Char(string="By")
    advance_received_amount_inr = fields.Float(string="Amount INR")
    advance_received_per = fields.Float(string="Amount %")

    ## Use in Phase 3
    ga_drawing_ready = fields.Selection([('Y','Y'),('N','N')], string="GA Drawing Ready", default="N")
    ga_drawing_ready_date = fields.Date(string="Date")
    ga_drawing_ready_by = fields.Char(string="By")
    ## Use in Phase 3
    ga_drawing_sent = fields.Selection([('Y','Y'),('N','N')], string="GA Drawing Sent", default="N")
    ga_drawing_sent_date = fields.Date(string="Date")
    ga_drawing_sent_by = fields.Char(string="By")

    ga_drawing_approved = fields.Selection([('Y','Y'),('N','N'),('NA','NA')], string="GA Drawing Approved", default='N')
    ga_drawing_approved_date = fields.Date(string="Date")
    ga_drawing_approved_by = fields.Char(string="By")

    ## Use in Phase 3
    qap_sent = fields.Selection([('Y','Y'),('N','N')], string="QAP Sent", default="N")
    qap_sent_date = fields.Date(string="Date")
    qap_sent_by = fields.Char(string="By")

    qap_approved = fields.Selection([('Y','Y'),('N','N'),('NA','NA')], string="QAP Approved", default="N")
    qap_approved_date = fields.Date(string="Date")
    qap_approved_by = fields.Char(string="By")

    order_completed = fields.Selection([('Y','Y'),('N','N')], string="Order Completed", default="N")
    order_completed_date = fields.Date(string="Date")
    order_completed_by = fields.Char(string="By")

    order_cancelled = fields.Selection([('Y','Y'),('N','N')], string="Order Cancelled", default="N")
    order_cancelled_date = fields.Date(string="Date")
    order_cancelled_by = fields.Char(string="By")

    mo_issued_lines = fields.One2many('mo.issued.lines', 'sale_order_id', string="MO Issued Lines")
    po_sent_lines = fields.One2many('po.sent.lines', 'sale_order_id', string="PO Sent")
    raw_material_received_lines = fields.One2many('raw.material.received.lines', 'sale_order_id', string="Raw Materials Received")
    # mo_production_completed_lines = fields.One2many('mo.production.completed.lines', 'sale_order_id', string="MO Production Completed")
    payment_received_lines = fields.One2many('payment.received.lines', 'sale_order_id', string="Payment Received")
    dispatch_lines = fields.One2many('dispatch.lines', 'sale_order_id', string="Dispatch")

    ## Revise So Fields
    new_revision_so_no = fields.Char(string="SO Revision No", readonly="1", copy=False)



    @api.multi
    def revise_so(self):
        """
        Logic for revising SO and assign increment no to new genearted Revesion
        """
        ## Get sequence for SO Revision
        inc_seq = 1
        if self.new_revision_so_no:
            split_name = self.new_revision_so_no.split('#')
            if self.name in split_name:
                # print int(split_name[-1]), type(int(split_name[-1])),'-----------split_name'
                inc_seq = int(split_name[-1]) + 1
                print inc_seq,'-----------inc_seq'
                self.new_revision_so_no = self.name + '#' + str(inc_seq)
        else:
            self.new_revision_so_no = self.name + '#' + str(inc_seq)
        return True

    @api.multi
    def sent_revise_so(self):
        '''
            This function opens a window to compose an email, with the edi sale template message loaded by default
            this function send revise templates emails

        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        ## Update Quotation Sent values for order status
        quotation_sent_vals = {
            'quotation_sent_date': self._get_current_date(),
            'quotation_sent_by': self._get_current_user(),
            'quotation_sent_no': self.new_revision_so_no,
            'sale_order_id': self.id
        }
        ## Create new line every time for quotation sent Revision
        self.quotation_sent_line_ids = [[0,0, quotation_sent_vals]]

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }



    @api.multi
    def _get_current_user(self):
        """ return current user of system """
        uid = self.env['res.users'].search([('id','=',self.env.uid)])
        user_name = uid.name
        return user_name

    @api.multi
    def _get_current_date(self):
        """ Get current date """
        current_date = datetime.datetime.now()
        return current_date

    @api.model
    def create(self, vals):
        vals.update({
            'rfq_received_date' : self._get_current_date(),
            'rfq_received_by' : self._get_current_user()
        })
        res = super(SaleOrder, self).create(vals)
        """
            Inherit function to assign RFQ Received Data
        """
        print vals, res,'-----------res create'
        # res.rfq_received_date = self._get_current_date(),
        # res.rfq_received_by = self._get_current_user(),
        return res


    # @api.multi
    # def rfq_received(self):
    #     self.write({
    #     'state': 'RFQ Received',
    #     'rfq_received_date': self._get_current_date(),
    #     'rfq_received_by': self._get_current_user(),
    #     })

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        ## Update Quotation Sent values for order status
        quotation_sent_vals = {
            'quotation_sent_date': self._get_current_date(),
            'quotation_sent_by': self._get_current_user(),
            'quotation_sent_no': self.name,
            'sale_order_id': self.id
        }
        ## Create new line every time for quotation sent Revision
        self.quotation_sent_line_ids = [[0,0, quotation_sent_vals]]

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def _get_po_received_for_so(self):
        return "Test"

    @api.multi
    def _get_mo(self):
        """
            Get Related MO for SO
        """
        mrp_obj = self.env['mrp.production']
        new_origin = self.name + ':WH: Stock -> CustomersMTO'
        mo_ids = mrp_obj.search([('origin','=',new_origin)])
        return mo_ids

    @api.multi
    def _get_po(self):
        """
            Get Related PO for SO
        """
        po_obj = self.env['procurement.order']
        new_origin = self.name + ':WH: Stock -> CustomersMTO'
        po_ids = po_obj.search([('origin','=',new_origin)])
        return po_ids

    @api.multi
    def _get_delivery_order(self):
        """
            Get Delivery Order for SO
        """
        picking_obj = self.env['stock.picking']
        picking_ids = picking_obj.search([('origin','=',self.name)])
        return picking_ids

    @api.multi
    def action_confirm(self):
        """
            Inherit function to add entries for order status
        """
        res = super(SaleOrder, self).action_confirm()
        ## Create PO receives lines for SO
        ## Customer PO received is same SO
        po_ids = self._get_po()
        for po_id in self:
            po_received_vals = {
                    'customer_po_received_date': self._get_current_date(),
                    'customer_po_received_by': self._get_current_user(),
                    'customer_po_received_no': po_id.name,
                    'sale_order_id':po_id.id,
                }
            ## Create lines and append here
            self.customer_po_received_line_ids=[[0, 0, po_received_vals]]

        ## Write values for order Acceptance of SO
        self.write({
            'order_accepted': 'Y',
            'order_accepted_date': self._get_current_date(),
            'order_accepted_by': self._get_current_user(),
        })

        ## Logic to get MO for related SO
        mo_ids = self._get_mo()
        for mo_id in mo_ids:
            mo_issued_vals = {
                    'mo_issued_date': self._get_current_date(),
                    'mo_issued_by': self._get_current_user(),
                    'mo_issued_no': mo_id.name,
                    'mo_production_completed': 'Y' if mo_id.state == 'done' else 'N',
                    'mrp_id': mo_id.id,
                    'sale_order_id':self.id,
                }
            ## Create lines and append here
            self.mo_issued_lines = [[0, 0, mo_issued_vals]]

        ## Logic to get MO for related SO
        picking_ids = self._get_delivery_order()
        for pick_id in picking_ids:
            picking_vals = {
                    'dispatch_date': self._get_current_date(),
                    'dispatch_by': self._get_current_user(),
                    'dispatch_dc_no': pick_id.name,
                    'stock_pick_id': pick_id.id,
                    'sale_order_id':self.id,
                }
            ## Create lines and append here
            self.dispatch_lines = [[0, 0, picking_vals]]
        return res

    # @api.multi
    # def customer_po_received(self):
    #     self.write({
    #     'state': 'Customer PO Received',
    #     'customer_po_received_date': self._get_current_date(),
    #     'customer_po_received_by': self._get_current_user(),
    #     })

    @api.multi
    def create_advance_received(self):
        self.write({
        'state': 'Advance Received',
        'advance_received': 'Y',
        'advance_received_date': self._get_current_date(),
        'advance_received_by': self._get_current_user(),
        })

    @api.multi
    def gad_approved(self):
        self.write({
        'state': 'GAD Approved',
        'ga_drawing_approved': 'Y',
        'ga_drawing_approved_date': self._get_current_date(),
        'ga_drawing_approved_by': self._get_current_user(),
        })

    @api.multi
    def create_qap_approved(self):
        self.write({
        'state': 'QAP Approved',
        'qap_approved': 'Y',
        'qap_approved_date': self._get_current_date(),
        'qap_approved_by': self._get_current_user(),
        })

    @api.multi
    def action_done(self):
        """
            Inherit function to make entries for So date
            under Order completed group
        """
        self.write({
        'state': 'done',
        'order_completed':'Y',
        'order_completed_date': self._get_current_date(),
        'order_completed_by': self._get_current_user(),
        })

    @api.multi
    def action_cancel(self):
        self.write({
            'order_cancelled': 'Y',
            'order_cancelled_date': self._get_current_date(),
            'order_cancelled_by': self._get_current_user()
        })
        return super(SaleOrder, self).action_cancel()



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    """ Inherit class for adding new fields on order line"""

    size = fields.Float(string="Size")
    moc = fields.Char(string="MOC")
    operation = fields.Char(string="Operation")
    pn = fields.Char(string="PN")
    line_delivery_date = fields.Date(string="Delivery Date")

class ClientDocLines(models.Model):
    _name = "client.doc.lines"
    ##For RFQ
    rfq_filename = fields.Char(string="File name")
    rfq_file = fields.Many2one('ir.attachment',string="RFQ")

    #For PO
    po_filename = fields.Char(string="File name")
    po_file = fields.Many2one('ir.attachment',string="PO")

    approved_ga_drawing_file = fields.Many2one('ir.attachment', string="Approved GA Drawing")
    approved_qa_plan_file = fields.Many2one('ir.attachment', string="Approved QA Plan")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class ERPDocLines(models.Model):
    _name = "erp.doc.lines"
    ##For RFQ
    quote_date = fields.Date(string="Quotation Date")
    quote_no = fields.Char(string="Quotation No")
    #For PO
    order_acc_date = fields.Date(string="Order Acceptance Date")
    order_acc_no = fields.Char(string="Order Acceptance No")
    tpi_call_date = fields.Date(string="TPI Call")
    test_cert_date = fields.Date(string="Test Certificates")
    delivery_challan_date = fields.Date(string="Delivery Challan Date")
    delivery_challan_no = fields.Char(string="Delivery Challan No")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_no = fields.Char(string="Invoice No")
    warr_certificate = fields.Char(string="Warranty Certificate")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class IvUserDocLines(models.Model):
    _name = "iv.user.doc.lines"

    ga_drawing_phase3 = fields.Date(string="GA Drawing")
    qa_plan_date_phase3 = fields.Date(string="QA Plan")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class MOIssuedLines(models.Model):
    _name = "mo.issued.lines"

    # mo_issued = fields.Selection([('Y','Y'),('N','N')], string="MO Issued")
    mo_issued_date = fields.Date(string="Date")
    mo_issued_by = fields.Char(string="By")
    mo_issued_no = fields.Char(string="No")
    mo_production_completed = fields.Selection([('Y','Y'),('N','N'),('Part','Part')], string="MO Production Completed")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    mrp_id = fields.Many2one('mrp.production', string="MRP Id")

class POSentLines(models.Model):
    _name = "po.sent.lines"

    po_sent = fields.Selection([('Y','Y'),('N','N')], string="PO Sent")
    po_sent_date = fields.Date(string="Date")
    po_sent_by = fields.Char(string="By")
    po_sent_vendor_name = fields.Char(string="Vendor Name")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class RawMaterailReceivedLines(models.Model):
    _name = "raw.material.received.lines"

    raw_material_received = fields.Selection([('Y','Y'),('N','N'),('Part','Part')], string="Raw Materials Received")
    raw_material_received_date = fields.Date(string="Date")
    raw_material_received_by = fields.Char(string="By")
    raw_material_received_vendor_name = fields.Char(string="Vendor Name")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

# class MOProductionCompletedLines(models.Model):
#     _name = "mo.production.completed.lines"
#
#     mo_production_completed= fields.Selection([('Y','Y'),('N','N'),('Part','Part')], string="MO Production Completed")
#     mo_production_completed_date = fields.Date(string="Date")
#     mo_production_completed_by = fields.Char(string="By")
#     mo_production_completed_mo_no = fields.Char(string="Mo No")
#     sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class PaymentReceivedLines(models.Model):
    _name = "payment.received.lines"

    payment_received = fields.Selection([('Y','Y'),('N','N')], string="Payment Received")
    payment_received_date = fields.Date(string="Date")
    payment_received_by = fields.Char(string="By")
    payment_received_amt_inr = fields.Float(string=" Amount INR")
    payment_received_amt_per = fields.Float(string="Amount %")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

class DispatchLines(models.Model):
    _name = "dispatch.lines"

    dispatch_date = fields.Date(string="Date")
    dispatch_by = fields.Char(string="By")
    dispatch_dc_no = fields.Char(string="DC No")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    ## Add referance of stock.delivery
    stock_pick_id = fields.Many2one('stock.picking', string="Sale Order")

class DocumentLines(models.Model):
    _name = "document.lines"
    DOCUMENT_TYPE = [
        ('RFQ','RFQ'),
        ('PO','PO'),
        ('Approved GA Drawing','Approved GA Drawing'),
        ('Approved QA Plan','Approved QA Plan'),
        ('Quotation','Quotation'),
        ('Order Acceptance','Order Acceptance'),
        ('TPI Call','TPI Call'),
        ('Test Certificates','Test Certificates'),
        ('Delivery Challan','Delivery Challan'),
        ('Invoice','Invoice'),
        ('Warranty Certificate','Warranty Certificate'),
        ('GA Drawing','GA Drawing'),
        ('QA Plan','QA Plan')]
    document_type = fields.Selection(DOCUMENT_TYPE, string="Document Type")
    document_date = fields.Date(string="Date")
    document_no = fields.Char(string="No")
    document_filename = fields.Char(string="File name")
    document_attachment = fields.Binary(string="Attach Document")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    @api.multi
    def _create_attachment_for_documents(self, vals):
        """
            Create attachment from uploaded files
            for All Documents Type File
            Rename uploaded file name with format
            document_type + so_no + client_name + doc_date
        """
        ## Add object here
        attachment_obj = self.env['ir.attachment']

        if vals and 'sale_order_id' in vals:
            ## get current So ID
            so_id = self.env['sale.order'].search([('id','=',vals.get('sale_order_id'))])
            ## vals for attachment of documents
            ir_attachment_vals = {
                'name': False,
                'type': 'binary',
                'datas_fname': False,
                'datas': False,
                'res_model': 'sale.order',
                'res_id': so_id.id,
                'res_name': so_id.name,
            }

        if vals and 'document_type' in vals and vals.get('document_attachment') != False:
            ## RFQ
            if vals.get('document_type') == 'RFQ':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                ## Rename file name with new format
                ## doc_name + SO_no + client_name + doc_date
                self.document_filename = attachment_id.name

            ##PO
            if vals.get('document_type') == 'PO':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## Approved GA Drawing
            if vals.get('document_type') == 'Approved GA Drawing':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ##Approved QA Plan
            if vals.get('document_type') == 'Approved QA Plan':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ##Quotation
            if vals.get('document_type') == 'Quotation':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ##Order Acceptance
            if vals.get('document_type') == 'Order Acceptance':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ##TPI Call
            if vals.get('document_type') == 'TPI Call':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ##Test Certificates
            if vals.get('document_type') == 'Test Certificates':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## Delivery Challan
            if vals.get('document_type') == 'Delivery Challan':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## Invoice
            if vals.get('document_type') == 'Invoice':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## Warranty Certificate
            if vals.get('document_type') == 'Warranty Certificate':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## GA Drawing
            if vals.get('document_type') == 'GA Drawing':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
            ## QA Plan
            if vals.get('document_type') == 'QA Plan':
                doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
                ir_attachment_vals.update({
                    'name' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas_fname' : vals.get('document_type') + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                    'datas': vals.get('document_attachment'),
                })
                attachment_id = attachment_obj.create(ir_attachment_vals)
                self.document_filename = attachment_id.name
        return True


    @api.model
    def create(self, vals):
        res = super(DocumentLines, self).create(vals)
        ## Call function to create attachments for uploaded documents
        res._create_attachment_for_documents(vals)
        return res

    @api.multi
    def _create_attachment_for_updated_documents(self, vals):
        ## Add object here
        attachment_obj = self.env['ir.attachment']

        if self.sale_order_id:
            ## get current So ID
            so_id = self.env['sale.order'].search([('id','=',self.sale_order_id.id)])
            ## vals for attachment of documents
            ir_attachment_vals = {
                'name': False,
                'type': 'binary',
                'datas_fname': False,
                'datas': False,
                'res_model': 'sale.order',
                'res_id': so_id.id,
                'res_name': so_id.name,
            }

        if vals and 'document_date' in vals:
            doc_dt = datetime.datetime.strptime(vals.get('document_date'), '%Y-%m-%d').strftime("%b %d %Y")
        else:
            doc_dt = datetime.datetime.strptime(self.document_date, '%Y-%m-%d').strftime("%b %d %Y")

        ## RFQ
        if self.document_type == 'RFQ':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name

        ## PO
        if self.document_type == 'PO':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Approved GA Drawing
        if self.document_type == 'Approved GA Drawing':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Approved QA Plan
        if self.document_type == 'Approved QA Plan':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Quotation
        if self.document_type == 'Quotation':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Order Acceptance
        if self.document_type == 'Order Acceptance':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## TPI Call
        if self.document_type == 'TPI Call':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name

        ## Test Certificates
        if self.document_type == 'Test Certificates':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name

        ## Delivery Challan
        if self.document_type == 'Delivery Challan':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Invoice
        if self.document_type == 'Invoice':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## Warranty Certificate
        if self.document_type == 'Warranty Certificate':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name

        ## GA Drawing
        if self.document_type == 'GA Drawing':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        ## QA Plan
        if self.document_type == 'QA Plan':
            ir_attachment_vals.update({
                'name' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas_fname' : self.document_type + '-' + so_id.name + '-' + so_id.partner_id.name + '-' + doc_dt,
                'datas': vals.get('document_attachment'),
            })
            attachment_id = attachment_obj.create(ir_attachment_vals)
            ## Rename file name with new format
            ## doc_name + SO_no + client_name + doc_date
            self.document_filename = attachment_id.name
        return True


    @api.multi
    def write(self, vals):
        res = super(DocumentLines, self).write(vals)
        if vals and 'document_attachment' in vals and vals.get('document_attachment') != False:
            self._create_attachment_for_updated_documents(vals)
        return res


class QuotationSentLine(models.Model):
    _name = 'quotation.sent.line'

    quotation_sent_date = fields.Date(string="Date")
    quotation_sent_by = fields.Char(string="By")
    quotation_sent_no = fields.Char(string="No")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")


class CustomerPoReceivedLine(models.Model):
    _name = 'customer.po.received.line'

    customer_po_received_date = fields.Date(string="Date")
    customer_po_received_by = fields.Char(string="By")
    customer_po_received_no = fields.Char(string="No")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
