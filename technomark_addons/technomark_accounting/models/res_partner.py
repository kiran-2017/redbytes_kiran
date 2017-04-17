# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_vat_tin = fields.Char(string="VAT TIN")


    @api.multi
    def write(self, vals):
        """ Logic for to assign vat tin to partners all child contacts"""
        for child in self.child_ids:
            child.partner_vat_tin = vals['partner_vat_tin']
        res = super(ResPartner, self).write(vals)
        return res
