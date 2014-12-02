from osv import osv, fields
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from math import ceil,floor
from datetime import datetime, timedelta


class special_commission(osv.osv):
    _name='special.commission'

    def onchange_field(self, cr, uid, ids, field, context=None):
        res = {}
        if not field:
            res['value']={'field_name':False}
        if field:
            data = self.pool.get('ir.model.fields').browse(cr, uid, field)
            if data.model=='sale.order.line':
                model = 'orderline'
            elif data.model == 'sale.order':
                model = 'order'
            elif data.model == 'commission.rules':
                model = 'rule'
            res['value'] = {'field_name':data.name}
        return res

    def onchange_model(self, cr, uid, ids, model, context=None):
        res = {}
        res['value']={'field_id':False,'field_name':False}
        return res

    def onchange_manager(self, cr, uid, ids, manager_field, context=None):
        res={}
        if not manager_field:
            res['value']={'sale_final_result':False}
        res['value']={'sale_final_result':manager_field}
        return res

    _columns = {
    'product_category_ids':fields.many2many('product.category','commission_categ_rel','commission_id','categ_id','Product Category'),
    'name':fields.char('Name',size=64,required=True),
    
    'model_id':fields.many2one('ir.model','Object',domain="[('model','in',['sale.order.line'])]"),
    'field_id':fields.many2one('ir.model.fields','Object Fields'),
    'field_name':fields.char('Field Name',size=64),

    'rule_one':fields.char('Rule One',size=255,required=True),
    'rule_two':fields.char('Rule Two',size=255),
    'rule_three':fields.char('Rule Three',size=255),
    'rule_four':fields.char('Rule Four',size=255),
    'rule_five':fields.char('Rule Five',size=255),
    'rule_six':fields.char('Rule Six',size=255),
    'commission_date':fields.date('Date',readonly=True),

    'condition_one':fields.char('Condition One',size=255),
    'condition_two':fields.char('Condition Two',size=255),
    'condition_three':fields.char('Condition Three',size=255),
    'condition_four':fields.char('Condition Four',size=255),
    'condition_five':fields.char('Condition Five',size=255),
    'condition_six':fields.char('Condition Six',size=255),
    'special_commission_rate':fields.float('Special Commission Rate'),
    'special_commission_val':fields.float('Special Commission'),
    'code_example':fields.text('Code Example', readonly=True),
    'result_example':fields.text('Result Example',readonly=True),
    'manager_field':fields.selection([('brand_manager','Brand Manager'),('regional_manger','Regional manager')],'Manager'),
    'sale_final_result':fields.char('Final Result',size=255,required=True),
    

    }
    _defaults={

    'commission_date':fields.date.context_today,

    'code_example': '''# Available variables:
    #----------------------
    # order: object containing the sale order
    # orderline: object containing the sale order line
    # Note: Condition can be define using logical operators['<','>','<=','>=','==','!=']
    eg 1:price_subtotal>100.00
    eg 2:rule1<100.00

    #Note: Rules can be define using Mathmetical operators['ceil','floor','-','+','*','/']
    eg 1:ceil(rule1)
    eg 2:price_subtotal-(misc_cost_total+attr_cost+product_cost)




    # Available variables:
    misc_cost_total,misc_sale_total,attr_cost,attr_sale,price_unit,price_subtotal,
    #----------------------

    # orderline: object containing the sale order line


    ''',
    'result_example':'''# Final Result= Brand Manager + above rule
                                          or
            Final Result= Regional Manager + above rule'''
    }



