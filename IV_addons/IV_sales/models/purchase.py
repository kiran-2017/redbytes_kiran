# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    """
        Inherit This function to create Raw material Received Againe4d any SO
        and create lines for that on SO
    """


    @api.multi
    def action_rfq_send(self):
        ## Inherit this method to create PO sent lines on res SO
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        if self.origin:
            ## Get So no for related Po and create Po sent lines on SO
            sale_order_ids = self._get_po_sent_lies()
        for sale_order_id in sale_order_ids:
            if sale_order_id:
                po_sent_vals = {
                        'po_sent_date': sale_order_id._get_current_date(),
                        'po_sent_by': sale_order_id._get_current_user(),
                        'po_sent_no': self.name,
                        'purchase_id': self.id,
                        'sale_order_id':sale_order_id.id,
                    }
                ## Create lines and append here
                sale_order_id.po_sent_lines = [[0, 0, po_sent_vals]]

        return {
            'name': _('Compose Email'),
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
    def _get_incoming_shipment(self):
        """
            Get Incoming Shipment Order for SO
        """
        picking_obj = self.env['stock.picking']

        picking_ids = picking_obj.search([('origin','=',self.name)])
        return picking_ids


    @api.multi
    def _get_po_sent_lies(self):
        """
            Get PO Sent for SO
        """
        so_obj = self.env['sale.order']
        so_list = []
        ## split multiple origin for related po
        origin_list = str(self.origin).split(',')
        if origin_list:
            for origin in origin_list:
                ## separate SO name form origin to get SO id
                split_origin = origin.split(':')
                if split_origin:
                    sale_order_id = so_obj.search([('name','=',split_origin[0].strip())])
                    if sale_order_id and sale_order_id not in so_list:
                        so_list.append(sale_order_id)
        return so_list

    @api.multi
    def button_confirm(self):

        so_obj = self.env['sale.order']
        po_sent_obj = self.env['po.sent.lines']

        res = super(PurchaseOrder, self).button_confirm()
        if self.origin:
            ## Get So no for related Po and create Po sent lines on SO
            sale_order_ids = self._get_po_sent_lies()
            for sale_order_id in sale_order_ids:
                if sale_order_id:
                    po_sent_vals = {
                            'po_sent_date': sale_order_id._get_current_date(),
                            'po_sent_by': sale_order_id._get_current_user(),
                            'po_sent_no': self.name,
                            'purchase_id': self.id,
                            'sale_order_id':sale_order_id.id,
                        }
                    ## Create lines and append here
                    po_sent_id = self.env['po.sent.lines'].search([('purchase_id','=',self.id),('sale_order_id','=',sale_order_id.id)])
                    if not po_sent_id:
                        sale_order_id.po_sent_lines = [[0, 0, po_sent_vals]]


        ## Logic to Raw material Lines
        po_sent_ids = po_sent_obj.search([('purchase_id','=',self.id)])
        picking_ids = self._get_incoming_shipment()
        for po_sent_id in po_sent_ids:
            for pick_id in picking_ids:
                picking_vals = {
                        'raw_material_received_date': so_obj._get_current_date(),
                        'raw_material_received_by': so_obj._get_current_user(),
                        'raw_material_received_no': pick_id.name,
                        'incoming_pick_id': pick_id.id,
                        'sale_order_id':po_sent_id.sale_order_id.id,
                    }
                ## Create lines and append here
                po_sent_id.sale_order_id.raw_material_received_lines = [[0, 0, picking_vals]]
        return res
