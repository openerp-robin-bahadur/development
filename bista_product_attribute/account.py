from osv import osv, fields
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from math import ceil,floor
from datetime import datetime, timedelta

class crm_case_section(osv.osv):
    _inherit="crm.case.section"
#    
    def create(self,cr,uid,vals,context=None):
        res=super(crm_case_section,self).create(cr,uid,vals,context)
        if vals['member_ids']:
            member_id=[x.id for x in self.browse(cr,uid,res).member_ids]
            for each in member_id:
                user_obj=self.pool.get('res.users').browse(cr,uid,each)
                sale_search=self.search(cr,uid,[('member_ids','in',each)])
                if sale_search:
                    for id in sale_search:
                        sale_obj=self.browse(cr,uid,id)
                        if id != res:
                            raise osv.except_osv(_('Error!'), _('User %s is Already assign to Sales Team %s')%(user_obj.name,sale_obj.name))
        return res

    def write(self,cr,uid,ids,vals,context=None):
        res=super(crm_case_section,self).write(cr,uid,ids,vals,context)
        if vals['member_ids']:
            for each in self.browse(cr,uid,ids):
                member_id=[x.id for x in each.member_ids]
                for m_id in member_id:
                    user_obj=self.pool.get('res.users').browse(cr,uid,m_id)
                    sale_search=self.search(cr,uid,[('member_ids','in',m_id)])
                    if sale_search:
                        for id in sale_search:
                            sale_obj=self.browse(cr,uid,id)
                            if id != each.id:
                                raise osv.except_osv(_('Error!'), _('User %s is Already assign to Sales Team %s')%(user_obj.name,sale_obj.name))
        return res

crm_case_section()

class product_category(osv.osv):
    _inherit='product.category'
    _columns={
    'account_lines_ids':fields.one2many('account.lines','product_categ_id','Account Lines')
    }

    def create(self,cr,uid,vals,context=None):
        if len(vals.get('account_lines_ids'))== 0:
            raise osv.except_osv(_('Error!'), _('There must be atleast one Sales Team defined'))
        return super(product_category,self).create(cr,uid,vals,context)

    def write(self,cr,uid,ids,vals,context=None):
        for each in self.browse(cr,uid,ids):
            res=super(product_category,self).write(cr,uid,ids,vals,context)
            if len(each.account_lines_ids) == 0:
                raise osv.except_osv(_('Error!'), _('There must be atleast one Sales Team defined'))
        return res
    
class account_lines(osv.osv):
    _name='account.lines'
    _columns={
    'sales_team_id':fields.many2one('crm.case.section','Sale Team',required=True),
    'income_account_id':fields.many2one('account.account','Income Account',required=True),
    'expense_account_id':fields.many2one('account.account','Expense Account',required=True),
    'product_categ_id':fields.many2one('product.category','Product Category'),
    }

