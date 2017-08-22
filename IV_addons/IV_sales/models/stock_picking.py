# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _create_dispatched_lines(self, backorder_picking, picking):
        sale_order_obj = self.env['sale.order']
        purchase_order_obj = self.env['purchase.order']
        dispatch_obj = self.env['dispatch.lines']
        po_sent_obj = self.env['po.sent.lines']
        raw_material_obj = self.env['raw.material.received.lines']
        so_ids = sale_order_obj.search([('name','=',picking.origin)])
        for so_id in so_ids:
            picking_vals = {
                    'dispatch_date': sale_order_obj._get_current_date(),
                    'dispatch_by': sale_order_obj._get_current_user(),
                    'dispatch_dc_no': backorder_picking.name,
                    'stock_pick_id': backorder_picking.id,
                    'sale_order_id':so_id.id,
                }
            ## Create lines and append here
            dispatch_obj.create(picking_vals)
            # sale_order_obj.dispatch_lines = [[0, 0, picking_vals]]

        ## Logic for Incoming shipment lines on SO
        po_ids = purchase_order_obj.search([('name','=',picking.origin)])
        for po_id in po_ids:
            po_sent_id = po_sent_obj.search([('purchase_id','=',po_id.id)])
            if po_sent_id:
                picking_vals = {
                        'raw_material_received_date': sale_order_obj._get_current_date(),
                        'raw_material_received_by': sale_order_obj._get_current_user(),
                        'raw_material_received_no': backorder_picking.name,
                        'incoming_pick_id': backorder_picking.id,
                        'sale_order_id':po_sent_id.sale_order_id.id,
                    }
                ## Create lines and append here
                raw_material_obj.create(picking_vals)

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        """ Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
        """
        # TDE note: o2o conversion, todo multi
        backorders = self.env['stock.picking']
        for picking in self:
            backorder_moves = backorder_moves or picking.move_lines
            if self._context.get('do_only_split'):
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
            else:
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
            if not not_done_bo_moves:
                continue
            backorder_picking = picking.copy({
                'name': '/',
                'move_lines': [],
                'pack_operation_ids': [],
                'backorder_id': picking.id
            })
            if backorder_picking:
                self._create_dispatched_lines(backorder_picking, picking)
            picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
            not_done_bo_moves.write({'picking_id': backorder_picking.id})
            if not picking.date_done:
                picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            backorder_picking.action_confirm()
            backorder_picking.action_assign()
            backorders |= backorder_picking
        return backorders
