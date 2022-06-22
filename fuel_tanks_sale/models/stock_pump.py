from odoo import models,fields,api,_

class StockPump(models.Model):
    _inherit = "stock.pump"

    def name_get(self):
        return [(pump.id, "%s (%s)" % (pump.name, pump.product_id.name)) for pump in self]

    def search(self, args, offset=0, limit=None, order=None, count=None):
        args = args or []
        args += [("product_id", "!=", False)]
        return super(StockPump, self).search(args, offset, limit, order, count)