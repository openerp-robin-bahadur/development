import time
from osv import osv, fields
import openerp.addons.decimal_precision as dp


class sale_price_history_wizard(osv.osv):
    _name='sale.price.history.wizard'


    def _history_line(self, line):
        return (0,0,{'order_line_id':line.order_line_id.id,
                          'cost_price':line.cost_price,
                          'sale_price':line.sale_price,
                          'attribute_id':line.attribute_id.id,
                          'calculation_method':line.calculation_method})

    def default_get(self, cr, uid, fields, context=None):
        history_line=[]
        if not context:
            context = {}
        line_ids = context.get('active_ids',[]) or []
        res = super(sale_price_history_wizard, self).default_get(cr, uid, fields, context)
        sale_price_history_id=self.pool.get('sale.price.history').search(cr,uid,[('order_line_id','in',line_ids)])
        for each in sale_price_history_id:
            sale_history=self.pool.get('sale.price.history').browse(cr,uid,each)
            history_line.append(self._history_line(sale_history))
            if history_line:
                res.update({'sale_price_history_ids':history_line})
        return res
    _columns={
    'sale_price_history_ids':fields.one2many('sale.price.history','sale_price_wizard_id','Sales Price History',readonly=True),
    }