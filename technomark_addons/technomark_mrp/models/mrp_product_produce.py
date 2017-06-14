# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    _description = "Record Production"

    @api.model
    def default_get(self, fields):
        """ Inherit this view to pass total product qty on produce pop up """

        res = super(MrpProductProduce, self).default_get(fields)
        stock_product_lot_obj = self.env['stock.production.lot']
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            #serial_raw = production.move_raw_ids.filtered(lambda x: x.product_id.tracking == 'serial')
            main_product_moves = production.move_finished_ids.filtered(lambda x: x.product_id.id == production.product_id.id)

            serial_finished = (production.product_id.tracking == 'serial')
            serial = bool(serial_finished)

            if serial_finished:
                quantity = 1.0
            else:
                quantity = production.product_qty - sum(main_product_moves.mapped('quantity_done'))
                quantity = quantity if (quantity > 0) else 0

            lines = []
            existing_lines = []
            for move in production.move_raw_ids.filtered(lambda x: (x.product_id.tracking != 'none') and x.state not in ('done', 'cancel')):
                if not move.move_lot_ids:
                    qty = quantity / move.bom_line_id.bom_id.product_qty * move.bom_line_id.product_qty
                    if move.product_id.tracking == 'serial':
                        while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                            lines.append({
                                'move_id': move.id,
                                'quantity': min(1,qty),
                                'quantity_done': 0.0,
                                'plus_visible': True,
                                'product_id': move.product_id.id,
                                'production_id': production.id,
                            })
                            qty -= 1
                    else:
                        lines.append({
                            'move_id': move.id,
                            'quantity': qty,
                            'quantity_done': 0.0,
                            'plus_visible': True,
                            'product_id': move.product_id.id,
                            'production_id': production.id,
                        })
                else:
                    existing_lines += move.move_lot_ids.filtered(lambda x: not x.lot_produced_id).ids

            res['serial'] = serial
            res['production_id'] = production.id
            ## To pass total MRP product qty to produce (Inherit view for)
            res['product_qty'] = production.product_qty #quantity
            res['product_id'] = production.product_id.id
            res['product_uom_id'] = production.product_uom_id.id
            res['consume_line_ids'] = map(lambda x: (0,0,x), lines) + map(lambda x:(4, x), existing_lines)
        return res

    @api.multi
    def check_finished_move_lots(self):
        lots = self.env['stock.move.lots']
        produce_move = self.production_id.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel'))
        if produce_move and produce_move.product_id.tracking != 'none':

            """ Hide because no need to add lot id mannualy create autometicaly on
                Record production button and assign lot id as per product qty
            # if not self.lot_id:
            #     raise UserError(_('You need to provide a lot for the finished product'))
            """
            existing_move_lot = produce_move.move_lot_ids.filtered(lambda x: x.lot_id == self.lot_id)
            if existing_move_lot:
                existing_move_lot.quantity += self.product_qty
                existing_move_lot.quantity_done += self.product_qty
            else:
                ## Logic to create lot ids as per product qty
                for i in range(int(self.product_qty)):
                    seq_vals = {
                            'name' : self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                            'product_id': self.product_id.id,
                            }
                    ## Create new sequqnce for MRP
                    new_lot_id = self.env['stock.production.lot'].create(seq_vals)
                    vals = {
                      'move_id': produce_move.id,
                      'product_id': produce_move.product_id.id,
                      'production_id': self.production_id.id,
                      'quantity': 1, #self.product_qty,
                      'quantity_done': 1, #self.product_qty,
                      'lot_id': new_lot_id.id, ## Assign to lot id here
                    }
                    lots.create(vals)
            for move in self.production_id.move_raw_ids:
                for movelots in move.move_lot_ids.filtered(lambda x: not x.lot_produced_id):
                    if movelots.quantity_done and self.lot_id:
                        #Possibly the entire move is selected
                        remaining_qty = movelots.quantity - movelots.quantity_done
                        if remaining_qty > 0:
                            default = {'quantity': movelots.quantity_done, 'lot_produced_id': self.lot_id.id}
                            new_move_lot = movelots.copy(default=default)
                            movelots.write({'quantity': remaining_qty, 'quantity_done': 0})
                        else:
                            movelots.write({'lot_produced_id': self.lot_id.id})
        return True
