# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    ## Add new field on work order form
    user_id = fields.Many2one('res.users', string="User")
