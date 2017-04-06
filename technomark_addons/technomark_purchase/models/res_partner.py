# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    """ Inherit class for adding new fields on partner form"""

    # Add fields
    frieght = fields.Char(string="Frieght")
