import time
from osv import osv, fields
import openerp.addons.decimal_precision as dp



class brand_manager_commission(osv.osv_memory):
    _name='brand.manager.commission'


    def cal_commission(self,cr,uid,ids,context=None):
        for each in self.browse(cr,uid,ids):
            sale_order_ids=self.pool.get('sale.order').search(cr,uid,[('x_billing_month','=',each.commission_month),('x_billing_year','=',each.commission_year)])
            print"===================sale order id mil gaya check karo=========",sale_order_ids
        return True
    def save_brand_manager(self,cr,uid,ids,context):
        return {'type':'ir.actions.act_window_close'}

    _columns = {
                'brand_manager_commission_line':fields.one2many('brand.manager.info','manager_commission_id','Commission Lines',readonly=True),
                'commission_month':fields.selection([('January','January'),('February','February'),('March','March'),('April','April'),('May','May'),('June','June'),('July','July'),('August','August'),('September','September'),('October','October'),('November','November'),('December','December')],'Billing Month',required=True),
                'commission_year':fields.integer('Billing Year',size=4,required=True),

                }
brand_manager_commission()

class brand_manager_info(osv.osv_memory):
    _name='brand.manager.info'

    _columns = {
                'brand_manager_id':fields.many2one('hr.employee','Manager'),
                'total_agi':fields.float('Total AGI'),
                'commission_val':fields.float('Commission'),
                'manager_commission_id':fields.many2one('brand.manager.commission','Brand Manager'),

                }

brand_manager_info()