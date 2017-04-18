# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    user_id = fields.Many2one('hr.employee', string="User")#, default=lambda self:self._context.get('active_id', False)
