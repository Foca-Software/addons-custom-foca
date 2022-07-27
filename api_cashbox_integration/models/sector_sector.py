from odoo import models

class SectorSector(models.Model):
    _inherit = "sector.sector"

    def inform_sector_stock(self, store_id=False):
        stock_list = []
        for sector in self:
            stock_quant_ids = sector.stock_quant_ids
            if store_id:
                stock_quant_ids = stock_quant_ids.filtered(
                    lambda x: x.location_id.lot_stock_warehouse_id.store_id.id
                    == store_id.id
                )

            quants = stock_quant_ids.read(["product_id", "quantity"])
            if quants:
                for item in quants:
                    del item["id"]
                    item['product_id'] = item['product_id'][0]
            stock_list.append({'sector':sector.code,'stock':quants})
        return stock_list