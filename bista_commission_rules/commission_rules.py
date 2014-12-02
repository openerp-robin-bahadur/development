# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from math import ceil,floor
from datetime import datetime, timedelta



class product_product(osv.osv):
    _inherit = 'product.product'
    
    _columns = {
                'commission_line':fields.one2many('commission.rules','product_id','Commission Line'),
                'miscellaneous_line':fields.one2many('miscellaneous.rules','product_id','Miscellaneous Line'),
                }

class commission_rules(osv.osv):
    _name = 'commission.rules'
    _description = "Commission Rules"

    _columns = {
                'name':fields.char('Name',size=64,required=True),
                'designation_id':fields.many2one('hr.job','Role',required=True),
                'condition_range_min': fields.float('Minimum Range', required=False, help="The minimum amount, applied for this rule."),
                'condition_range_max': fields.float('Maximum Range', required=False, help="The maximum amount, applied for this rule."),
                'amount_select':fields.selection([
                    ('percentage','Percentage (%)'),
                    ('fix','Fixed Amount'),
                    ('code','Python Code'),
                ],'Amount Type', select=True, help="The computation method for the rule amount."),
                'amount_fix': fields.float('Fixed Amount', digits_compute=dp.get_precision('Payroll'),),
                'amount_percentage': fields.float('Percentage (%)', digits_compute=dp.get_precision('Payroll Rate'), help='For example, enter 50.0 to apply a percentage of 50%'),
                'amount_python_compute':fields.text('Python Code'),
                'condition_python':fields.text('Python Condition', readonly=False, help='Applied this rule for calculation if condition is true. You can specify condition like total amount > 1000.'),
                'code_example':fields.text('Code Example', readonly=True),
                'note':fields.text('Description'),
                'product_id':fields.many2one('product.product','Product Commission'),
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
     }
    
    _defaults = {

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
     }
    
    
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


    def create(self,cr,uid,vals,context=None):
        res=super(commission_rules,self).create(cr,uid,vals,context)
        expression=['{','}','%','$','&','[',']',',','?','\\','<','>','<=','>=','==','!=']
        rule_field=['rule_one','rule_two','rule_three','rule_four','rule_five','rule_six']
        logic_exp=['{','}','%','$','&','[',']',',','?','\\','%']
        condition_field=['condition_one','condition_two','condition_three','condition_four','condition_five','condition_six']
        for condition in condition_field:
            condition_vals=vals.get(condition)
            if condition_vals:
                for logic in logic_exp:
                    if logic in condition_vals:
                        raise osv.except_osv(_('Error!'),
                _('invalid expression %s for defining Condition')%(logic))

        for rule in rule_field:
            rule_vals=vals.get(rule)
            if rule_vals:
                for exp in expression:
                    if exp in rule_vals:
                         raise osv.except_osv(_('Error!'),
                _('invalid expression %s for defining rule')%(exp))

        return res

    def write(self,cr,uid,ids,vals,context=None):
        res=super(commission_rules,self).write(cr,uid,ids,vals,context)
        expression=['{','}','%','$','&','[',']',',','?','\\','<','>','<=','>=','==','!=']
        rule_field=['rule_one','rule_two','rule_three','rule_four','rule_five','rule_six']
        logic_exp=['{','}','%','$','&','[',']',',','?','\\','%']
        condition_field=['condition_one','condition_two','condition_three','condition_four','condition_five','condition_six']
        for condition in condition_field:
            if vals.get(condition):
                condition_vals=vals.get(condition)
                for logic in logic_exp:
                    if logic in condition_vals:
                        raise osv.except_osv(_('Error!'),
                _('invalid expression %s for defining Condition')%(logic))

        for rule in rule_field:
            if vals.get(rule):
                rule_vals=vals.get(rule)
                for exp in expression:
                    if exp in rule_vals:
                        raise osv.except_osv(_('Error!'),
                        _('invalid expression %s for defining rule')%(exp))
        return res

class miscellaneous_rules(osv.osv):
    _name='miscellaneous.rules'

    _description = "Miscellaneous Rules"

    _columns = {
                'name':fields.char('Name',size=64,required=True),
                'partner_ids':fields.many2many('res.partner','misc_partner_rel','misc_id','partner_id','Customers'),
                'condition_range_min': fields.float('Minimum Range', required=False, help="The minimum amount, applied for this rule."),
                'condition_range_max': fields.float('Maximum Range', required=False, help="The maximum amount, applied for this rule."),
                'amount_select':fields.selection([
                    ('percentage','Percentage (%)'),
                    ('fix','Fixed Amount'),
                    ('code','Python Code'),
                ],'Amount Type', select=True, help="The computation method for the rule amount."),
                'amount_fix': fields.float('Fixed Amount', digits_compute=dp.get_precision('Payroll'),),
                'amount_percentage': fields.float('Percentage (%)', digits_compute=dp.get_precision('Payroll Rate'), help='For example, enter 50.0 to apply a percentage of 50%'),
                'amount_python_compute':fields.text('Python Code'),
                'condition_python':fields.text('Python Condition', readonly=False, help='Applied this rule for calculation if condition is true. You can specify condition like total amount > 1000.'),
                'code_example':fields.text('Code Example', readonly=True),
                'note':fields.text('Description'),
                'product_id':fields.many2one('product.product','Product Miscellaneous Rules'),
                'model_id':fields.many2one('ir.model','Object',domain="[('model','in',['miscellaneous.rules','sale.order.line'])]"),
                'field_id':fields.many2one('ir.model.fields','Object Fields'),
                'field_name':fields.char('Field Name',size=64),

                'rule_one':fields.char('Rule One',size=255,required=True),
                'rule_two':fields.char('Rule Two',size=255),
                'rule_three':fields.char('Rule Three',size=255),
                'rule_four':fields.char('Rule Four',size=255),
                'rule_five':fields.char('Rule Five',size=255),
                'rule_six':fields.char('Rule Six',size=255),

                'condition_one':fields.char('Condition One',size=255),
                'condition_two':fields.char('Condition Two',size=255),
                'condition_three':fields.char('Condition Three',size=255),
                'condition_four':fields.char('Condition Four',size=255),
                'condition_five':fields.char('Condition Five',size=255),
                'condition_six':fields.char('Condition Six',size=255),
     }

    _defaults = {


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
     }


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
            res['value'] = {'field_name':model +'.'+ data.name}
        return res

    def onchange_model(self, cr, uid, ids, model, context=None):
        res = {}
        res['value']={'field_id':False,'field_name':False}
        return res

   


    