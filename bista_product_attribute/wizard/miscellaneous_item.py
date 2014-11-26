import time
from osv import osv, fields
import openerp.addons.decimal_precision as dp


class miscellaneous_wizard(osv.osv_memory):
    _name='miscellaneous.wizard'


    def _misc_line(self, line):
        return (0,0,{'miscellaneous_id':line.miscellaneous_id.id,
                          'misc_cost_price':line.misc_cost_price,
                          'misc_sales_price':line.misc_sales_price})

    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        line_ids = context.get('active_ids',[]) or []
        misc_line = []
        res = super(miscellaneous_wizard, self).default_get(cr, uid, fields, context)
        for val in self.pool.get('sale.order.line').browse(cr, uid, line_ids):
            if 'product_id' in fields:
                res.update({'product_id':val.product_id and val.product_id.id or False})
            if 'line_id' in fields:
                res.update({'line_id':val.id})
            if 'miscellaneous_item_line' in fields:
                for sline in val.miscellaneous_line:
                    misc_line.append(self._misc_line(sline))
                if misc_line:
                    res.update({'miscellaneous_item_line':misc_line})
        return res
    
    _columns={
              'miscellaneous_item_line':fields.one2many('miscellaneous.wizard.line','misc_wiz_id','Miscellaneous Item'),
              'line_id':fields.many2one('sale.order.line','Sale Order Line'),
              'product_id':fields.many2one('product.product','Product'),
            }

    def save_miscellaneous_item(self, cr, uid, ids, context=None):
        misc_line = []
        item_ids = []
        total_misc_ids = []
        item_obj = self.pool.get('miscellaneous.line')
        for val in self.browse(cr, uid, ids):
            for line in val.miscellaneous_item_line:
                total_misc_ids.append(line.miscellaneous_id.id)
            del_item_ids = item_obj.search(cr, uid, [('line_id','=',val.line_id.id),('miscellaneous_id','not in',total_misc_ids)])
            if del_item_ids:
                item_obj.unlink(cr, uid, del_item_ids)
            for line in val.miscellaneous_item_line:
                for check in val.miscellaneous_item_line:
                    item_ids = item_obj.search(cr, uid, [('line_id','=',val.line_id.id),('miscellaneous_id','=',line.miscellaneous_id.id)])
                    if item_ids:
                        break
                if not item_ids:
                    item_obj.create(cr,uid,{'line_id':val.line_id.id,'miscellaneous_id':line.miscellaneous_id.id,
                          'misc_cost_price':line.misc_cost_price,'misc_sales_price':line.misc_sales_price})
                else:
                    item_obj.write(cr,uid,item_ids, {'miscellaneous_id':line.miscellaneous_id.id,
                          'misc_cost_price':line.misc_cost_price,'misc_sales_price':line.misc_sales_price})


            total_sale = 0.0
            total_cost = 0.0
            for line in val.line_id.miscellaneous_line:
                total_sale += line.misc_sales_price
                total_cost += line.misc_cost_price
            self.pool.get('sale.order.line').write(cr,uid,[val.line_id.id],{'misc_sale_total':total_sale,'misc_cost_total':total_cost})
        return {'type':'ir.actions.act_window_close'}
    
    
class miscellaneous_wizard_line(osv.TransientModel):
    _name='miscellaneous.wizard.line'


    _columns = {
                'miscellaneous_id':fields.many2one('miscellaneous.items','Miscellaneous Items',required=True),
                'misc_wiz_id':fields.many2one('miscellaneous.wizard','Miscellaneous'),
                'misc_cost_price':fields.float('Cost Price',digits=(16,2),required=True),
                'misc_sales_price':fields.float('Sales Price',digits=(16,2),required=True),
                }

    def onchange_miscellaneous_id(self,cr, uid, ids, miscellaneous, context=None):
        v = {}
        if miscellaneous:
            item = self.pool.get('miscellaneous.items').browse(cr,uid,miscellaneous)
            v['misc_cost_price'] = item.cost_price
            v['misc_sales_price'] = item.sales_price
        return {'value': v}
