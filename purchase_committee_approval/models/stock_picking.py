# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.picking'


    def action_set_quantities_to_reservation(self):
        super(StockMove, self).action_set_quantities_to_reservation()
        for line in self.move_ids_without_package:
            line.check_accept_purchase_qty()
