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
    def _get_incoming_shipment(self):
        """
            Get Incoming Shipment Order for SO
        """
        picking_obj = self.env['stock.picking']

        picking_ids = picking_obj.search([('origin','=',self.name)])
        return picking_ids


    @api.multi
    def button_confirm(self):

        so_obj = self.env['sale.order']
        po_sent_obj = self.env['po.sent.lines']

        res = super(PurchaseOrder, self).button_confirm()
        ## Logic to Raw material Lines

        po_sent_ids = po_sent_obj.search([('purchase_id','=',self.id)])
        picking_ids = self._get_incoming_shipment()
        print picking_ids,'---------picking_ids'
        print po_sent_ids,'----po_sent_id'
        for po_sent_id in po_sent_ids:
            for pick_id in picking_ids:
                print po_sent_id.sale_order_id,'------po_sent_id.sale_order_id'
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
