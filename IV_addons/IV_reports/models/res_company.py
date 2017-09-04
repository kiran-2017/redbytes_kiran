# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    """ Inherit this class for adding new fields on company form"""

    #Add cst on company view
    cst = fields.Char(string="CST")
