# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
