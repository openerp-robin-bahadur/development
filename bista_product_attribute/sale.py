from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp.osv import orm, fields

import logging
_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
    _inherit = "sale.order"


    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                if line.sold_for==False:
                    f_val=self.pool.get('sale.order.line')._sold_amount(cr, uid,[line.id],field_name,arg,context)
                    val1 += f_val[line.id]
                else:
                    val1 += line.sold_for
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def add_product_order_line(self,cr,uid,ids,context=None):
            read_data={}
            vals={}
            sales_price=0
            sales_price_per_unit = 0
            sales_price_per_order_line = 0
            sale_data=self.browse(cr,uid,ids[0])
            attr_name_in_product=[]
            attr_type_in_product=[]
            if sale_data.add_product_id.attribute_set_id:
                attribute_set_val=sale_data.add_product_id.attribute_set_id.attribute_group_ids
                for each in attribute_set_val:
                    for y in each.attribute_ids:
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_id.attribute_type)
                read_data=self.pool.get('product.product').read(cr,uid,[sale_data.add_product_id.id],attr_name_in_product)
                read_data = read_data[0]
            if sale_data.add_product_id:
                vals.update({'product_id':sale_data.add_product_id.id,
                'order_id':sale_data.id,
                'name':sale_data.add_product_id.name,
                'attribute_set_id':sale_data.add_product_id.attribute_set_id and sale_data.add_product_id.attribute_set_id.id or False,
                'product_cost':sale_data.add_product_id.standard_price,
                })

                for each in read_data:
                    if each in attr_name_in_product:
                        i = attr_name_in_product.index(each)
                        if attr_type_in_product[i] == 'select':
                            if read_data[each]:
                                read_data[each] = read_data[each][0]
                                sales_price_select=self.pool.get('attribute.option').browse(cr,uid,read_data[each]).sales_price
                                calculation_method = self.pool.get('attribute.option').browse(cr,uid,read_data[each]).price
                                if calculation_method:
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_select
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_select
                                    else:
                                        pass
                        elif attr_type_in_product[i] == 'multiselect':
                            if read_data[each]:
                                for each_attr_id in read_data[each]:
                                    sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price
                                    calculation_method = self.pool.get('attribute.option').browse(cr,uid,each_attr_id).price
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_multi
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_multi
                                    else:
                                        pass

                                read_data[each] = [(6,0,read_data[each])]
                            else:
                                read_data[each] = [(6,0,[])]
                        else:
                            search_id=self.pool.get('attribute.attribute').search(cr,uid,[('model','=','product.product'),('name','=',each)])
                            try:
                                sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
                                calculation_method = self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].price
                                if read_data[each]:
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_other
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_other
                                    else:
                                        pass
                            except:
                                pass
                            
                sales_price = self.pool.get('product.product').browse(cr,uid,sale_data.add_product_id.id).list_price
                vals.update(read_data)
                vals.update({'price_unit':sales_price+sales_price_per_unit,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})

                self.pool.get('sale.order.line').create(cr,uid,vals)
                self.write(cr,uid,ids,{'add_product_id':False})
            return True

    def add_template_order_line(self,cr,uid,ids,context=None):
        try:
            sales_price=0
            sales_price_per_unit = 0
            sales_price_per_order_line = 0
            vals={}
            sale_data=self.browse(cr,uid,ids[0])
            attr_name_in_product=[]
            attr_type_in_product=[]

            if sale_data.add_product_temp_id.attribute_id:
                attribute_set_val=sale_data.add_product_temp_id.attribute_id.attribute_group_ids
                for each in attribute_set_val:
                    for y in each.attribute_ids:
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_id.attribute_type)
            read_data=self.pool.get('base.product.template').read(cr,uid,[sale_data.add_product_temp_id.id],attr_name_in_product)
            read_data = read_data[0]
            if sale_data.add_product_temp_id:
                vals.update({'product_id':sale_data.add_product_temp_id.product_id.id,
                'order_id':sale_data.id,
                'name':sale_data.add_product_temp_id.name,
                'attribute_set_id':sale_data.add_product_temp_id.attribute_id and sale_data.add_product_temp_id.attribute_id.id or False,
                'product_cost':sale_data.add_product_id.standard_price,
                })

                for each in read_data:
                    if each in attr_name_in_product:
                        i = attr_name_in_product.index(each)
                        if attr_type_in_product[i] == 'select':
                            if read_data[each]:
                                read_data[each] = read_data[each][0]
                                sales_price_select=self.pool.get('attribute.option').browse(cr,uid,read_data[each]).sales_price
                                calculation_method = self.pool.get('attribute.option').browse(cr,uid,read_data[each]).price
                                if calculation_method:
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_select
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_select
                                    else:
                                        pass
                            else:
                                pass
                        elif attr_type_in_product[i] == 'multiselect':
                            if read_data[each]:
                                for each_attr_id in read_data[each]:
                                    sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price
                                    calculation_method = self.pool.get('attribute.option').browse(cr,uid,each_attr_id).price
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_multi
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_multi
                                    else:
                                        pass
                                read_data[each] = [(6,0,read_data[each])]
                            else:
                                read_data[each] = [(6,0,[])]
                        else:
                            search_id=self.pool.get('attribute.attribute').search(cr,uid,[('model','=','base.product.template'),('name','=',each)])
                            sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
                            try:
                                sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
                                calculation_method = self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].price
                                if read_data[each]:
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_other
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_other
                                    else:
                                        pass
                            except:
                                pass
                sales_price = self.pool.get('product.product').browse(cr,uid,sale_data.add_product_temp_id.product_id.id).list_price
                vals.update(read_data)
                vals.update({'price_unit':sales_price+sales_price_per_unit,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})
                vals.pop('id')
                self.pool.get('sale.order.line').create(cr,uid,vals)
                self.write(cr,uid,ids,{'add_product_temp_id':False})
            return True
        except:
            pass

    def add_bundle_order_line(self,cr,uid,ids,context=None):
        if self.browse(cr,uid,ids[0]).add_product_bundle_id:

            sale_data=self.browse(cr,uid,ids[0])
            for each_template in sale_data.add_product_bundle_id.template_id:
                vals={}
                attr_name_in_product=[]
                attr_type_in_product=[]
                sales_price=0
                sales_price_per_unit = 0
                sales_price_per_order_line = 0
                attribute_set_val=each_template.attribute_id.attribute_group_ids
                for each in attribute_set_val:
                    for y in each.attribute_ids:
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_id.attribute_type)
                read_data=self.pool.get('base.product.template').read(cr,uid,[each_template.id],attr_name_in_product)
                read_data = read_data[0]
#                template_ids_val = each_template.id
                vals.update({'product_id':each_template.product_id.id,
                'order_id':sale_data.id,
                'name':each_template.name,
                'attribute_set_id':each_template.attribute_id and each_template.attribute_id.id or False,
                'product_cost':sale_data.add_product_id.standard_price,
                })
                for each1 in read_data:
                    if each1 in attr_name_in_product:
                        i = attr_name_in_product.index(each1)
                        if attr_type_in_product[i] == 'select':
                            if read_data[each1]:
                                read_data[each1] = read_data[each1][0]
                                sales_price_select=self.pool.get('attribute.option').browse(cr,uid,read_data[each1]).sales_price
                                calculation_method = self.pool.get('attribute.option').browse(cr,uid,read_data[each1]).price
                                if calculation_method:
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_select
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_select
                                    else:
                                        pass
                            else:
                                pass
                        elif attr_type_in_product[i] == 'multiselect':
                            if read_data[each1]:
                                for each_attr_id in read_data[each1]:
                                    sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price
                                    calculation_method = self.pool.get('attribute.option').browse(cr,uid,each_attr_id).price
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_multi
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_multi
                                    else:
                                        pass
                                read_data[each1] = [(6,0,read_data[each1])]
                            else:
                                read_data[each1] = [(6,0,[])]
                        else:
                            search_id = self.pool.get('attribute.attribute').search(cr,uid,[('model','=','product.product'),('name','=',each1)])
                            sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
                            calculation_method = self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].price
                            if read_data[each1]:
                                if calculation_method == "per_unit":
                                    sales_price_per_unit += sales_price_other
                                elif calculation_method == "based_order_lines":
                                    sales_price_per_order_line += sales_price_other
                                else:
                                    pass
#                             
                sales_price = self.pool.get('product.product').browse(cr,uid,each_template.product_id.id).list_price
                vals.update(read_data)
                vals.update({'price_unit':sales_price+sales_price_per_unit,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})
                vals.pop('id')
                self.pool.get('sale.order.line').create(cr,uid,vals)
                self.write(cr,uid,ids,{'add_product_bundle_id':False})
            return True

#         
    def onchange_manufacture_id(self, cr, uid, ids, x_manufacturer, context=None):
       v = {}
       v['x_franchise']=False
       return {'value': v}


    def onchange_guarantee_type_id(self, cr, uid, ids, x_guarantee_type_id, context=None):
       v = {}
       if x_guarantee_type_id:
           verbiage_info= self.pool.get('guarantee.type').browse(cr,uid,x_guarantee_type_id).verbiage
           if verbiage_info:
                   v['x_guarantee_verbiage'] = verbiage_info
       return {'value': v}

    def onchange_company_id(self, cr, uid, ids,x_signing_company_id , context=None):
       v = {}
       v['x_signing_contact_id']=False
       return {'value': v}
   
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res =super(sale_order,self).onchange_partner_id(cr,uid,ids,part,context)
        if part:
            if self.pool.get('res.partner').browse(cr,uid,part).is_company:
                res['value'].update({'x_signing_company_id':part})
            else:
                res['value'].update({'x_signing_company_id':False})
        return res

    def onchange_billing_month(self, cr, uid, ids, month, context=None):
        v={}
        if month:
            pr_year=datetime.now().year-1
            curr_year=datetime.now().year
            next_year=datetime.now().year+1
            pr_dt = str(pr_year)+'-'+str(month) + '-1'
            cr_dt = str(curr_year)+'-'+str(month) + '-1'
            nx_dt = str(next_year)+'-'+str(month) + '-1'
            pr_date=datetime.strptime(pr_dt,"%Y-%B-%d")
            cr_date=datetime.strptime(cr_dt,"%Y-%B-%d")
            nx_date=datetime.strptime(nx_dt,"%Y-%B-%d")
            curr_date=datetime.strptime(time.strftime("%Y-%B-%d"),"%Y-%B-%d")
            if cr_date > curr_date:
                a=(cr_date - curr_date).days
            else:
                a=(curr_date - cr_date).days
            b=(curr_date - pr_date).days
            c=(nx_date - curr_date).days
            days=min(a,b,c)
            if days==a:
                v.update({'x_billing_year':curr_year})
            elif days==b:
                v.update({'x_billing_year':pr_year})
            else:
                v.update({'x_billing_year':next_year})

        return {'value': v}

    _columns = {

        'add_product_id':fields.many2one('product.product','Product',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'add_product_temp_id':fields.many2one('base.product.template','Product Template',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'add_product_bundle_id':fields.many2one('base.product.bundle','Product Bundle',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_billing_vendor_id':fields.many2one('res.partner','Billing Vendor',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_manager_id':fields.many2one('res.users','Sales Manager',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_cs_rep_id':fields.many2one('res.users','Client Service Rep',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_billing_month':fields.selection([('January','January'),('February','February'),('March','March'),('April','April'),('May','May'),('June','June'),('July','July'),('August','August'),('September','September'),('October','October'),('November','November'),('December','December')],'Billing Month',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_billing_year':fields.integer('Billing Year',size=4,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_coop':fields.many2one('coop.info','Coop',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_dealer_code':fields.char('Dealer Code',size=32,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_additional_code':fields.char('Additional Code',size=32,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_call_source':fields.boolean('Call Source',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_guarantee_type_id':fields.many2one('guarantee.type','Guarantee Type',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_guarantee_verbiage':fields.text('Guarantee Verbiage',size=1024,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_insurance_amount':fields.float('Insurance Amount',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_performance_based':fields.boolean('Performance Based',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_performance_tracking':fields.boolean('Performance Tracking',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_suppress_dms':fields.boolean('Suppress DMS',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_signing_company_id':fields.many2one('res.partner','Signing Company',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_signing_contact_id':fields.many2one('res.partner','Signing Contact',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_special_notes':fields.text('Special Notes',size=64,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_manufacturer':fields.many2one('manufacture.info','Manufacturer',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_franchise':fields.many2one('franchise.info','Franchise',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_campaign_theme_id':fields.many2one('campaign.theme',"Campaign Theme",states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'x_signed_flag':fields.boolean('Signed'),
        'x_payment_due_date':fields.date('Due Date',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'old_price_total':fields.float("old price"),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty','misc_sale_total','misc_cost_total','price_per_line','price_per_unit'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty','misc_sale_total','misc_cost_total','price_per_line','price_per_unit'], 10),
            },
            multi='sums', help="The total amount."),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default={}
        default.update({'state':'draft',
                        'x_signed_flag':False,
                        })
        return super(sale_order,self).copy(cr,uid,id,default,context)

sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _attr_grp_ids(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for i in ids:
            set_id = self.read(cr, uid, [i], fields=['attribute_set_id'],
                     context=context)[0]['attribute_set_id']
            if not set_id:
                res[i] = []
            else:
                res[i] = self.pool.get('attribute.group').search(cr, uid,
                      [('attribute_set_id', '=', set_id[0])])
        return res

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        price_misc_cost = 0
        price_per_line = 0
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price_misc_cost = line.misc_sale_total * (1 - (line.discount or 0.0) / 100.0)
            price_per_line = line.price_per_line * (1 - (line.discount or 0.0) / 100.0)
#             Add the Attributs price which are defined to be calculated on per unit of product
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id, price_misc_cost,price_per_line)
            taxes['total'] = taxes['total'] + price_misc_cost+price_per_line
            taxes['total_included'] = taxes['total_included'] + price_misc_cost+price_per_line
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    def _sold_amount(self, cr, uid, ids, field_name, arg, context=None):
        print" sold for===="
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        price_misc_cost = 0
        price_per_line = 0
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price_misc_cost = line.misc_sale_total * (1 - (line.discount or 0.0) / 100.0)
            price_per_line = line.price_per_line * (1 - (line.discount or 0.0) / 100.0)
#             Add the Attributs price which are defined to be calculated on per unit of product
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id, price_misc_cost,price_per_line)
            taxes['total'] = taxes['total'] + price_misc_cost+price_per_line
            taxes['total_included'] = taxes['total_included'] + price_misc_cost+price_per_line
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    def _set_sold_amount(self, cr, uid, ids, name, value, arg, context=None):
        print" reverse function"
        if ids and (value==0 or value>0):
            pos="""update sale_order_line set
                        sold_for=%d
                    where
                        id=%d"""%(value,ids)
            cr.execute(pos)
        return True

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    def _cal_attr_unit_sale_price(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        attr_obj = self.pool.get('attribute.attribute')
        option_obj = self.pool.get('attribute.option')
        for val in self.browse(cr, uid, ids):
            price_per_unit = 0
            price_per_order_line = 0
            attr_names = []
            so_line_attrs = {}
            if val.attribute_set_id:
                for each_grp_id in val.attribute_set_id.attribute_group_ids:
                    for each_attr_id in each_grp_id.attribute_ids:
                        attr_names.append(each_attr_id.attribute_id.name)
            if len(attr_names)>0:
                so_line_data = self.read(cr, uid, val.id, attr_names)
                for each in attr_names:
                    if isinstance(so_line_data[each],tuple):
                        if len(so_line_data[each]):
                            attr_option_data = option_obj.read(cr, uid, so_line_data[each][0], [])
                            if attr_option_data['price'] == 'per_unit':
                                 price_per_unit += attr_option_data['sales_price']
                            elif attr_option_data['price'] == "based_order_lines":
                                price_per_order_line += attr_option_data['sales_price']

                    elif isinstance(so_line_data[each],list):
                        for attr_option_data in option_obj.read(cr, uid, so_line_data[each], []):
                            if attr_option_data['price'] == 'per_unit':
                                price_per_unit += attr_option_data['sales_price']
                            elif attr_option_data['price'] == "based_order_lines":
                                price_per_order_line += attr_option_data['sales_price']

                    else:
                        attr_id = attr_obj.search(cr, uid, [('name','=',each),('model','=','sale.order.line')])
                        if attr_id:
                            attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_id[0])], limit=1)
                            if attr_option_obj:
                                attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])
                            if attr_option_data['price'] == 'per_unit':
                                price_per_unit += attr_option_data['sales_price']
                            elif attr_option_data['price'] == "based_order_lines":
                                price_per_order_line += attr_option_data['sales_price']
            res[val.id] = price_per_unit + price_per_order_line/val.product_uom_qty
        return res
    
    def _cal_attr_unit_cost_price(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        attr_obj = self.pool.get('attribute.attribute')
        option_obj = self.pool.get('attribute.option')
        for val in self.browse(cr, uid, ids):
            price_per_unit = 0
            price_per_order_line = 0
            attr_names = []
            if val.attribute_set_id:
                for each_grp_id in val.attribute_set_id.attribute_group_ids:
                    for each_attr_id in each_grp_id.attribute_ids:
                        attr_names.append(each_attr_id.attribute_id.name)
            if len(attr_names)>0:
                so_line_data = self.read(cr, uid, val.id, attr_names)
                for each in attr_names:
                    if isinstance(so_line_data[each],tuple):
                        if len(so_line_data[each]):
                            attr_option_data = option_obj.read(cr, uid, so_line_data[each][0], [])
                            if attr_option_data['price'] == 'per_unit':
                                 price_per_unit += attr_option_data['cost_price']
                            elif attr_option_data['price'] == "based_order_lines":
                                price_per_order_line += attr_option_data['cost_price']

                    elif isinstance(so_line_data[each],list):
                        for attr_option_data in option_obj.read(cr, uid, so_line_data[each], []):
                            if attr_option_data['price'] == 'per_unit':
                                price_per_unit += attr_option_data['cost_price']
                            elif attr_option_data['price'] == "based_order_lines":
                                price_per_order_line += attr_option_data['cost_price']

                    else:
                        attr_id = attr_obj.search(cr, uid, [('name','=',each),('model','=','sale.order.line')])
                        if attr_id:
                            attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_id[0])], limit=1)
                            if attr_option_obj:
                                attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])
                            if attr_option_data:
                                if attr_option_data['price'] == 'per_unit':
                                    price_per_unit += attr_option_data['cost_price']
                                elif attr_option_data['price'] == "based_order_lines":
                                    price_per_order_line += attr_option_data['cost_price']
            res[val.id] = price_per_unit + price_per_order_line/val.product_uom_qty
        return res


    _columns = {
        'attribute_group_ids': fields.function(_attr_grp_ids, type='many2many',
        relation='attribute.group', string='Groups'),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'product_uom_qty': fields.integer('Quantity', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'price_per_unit':fields.float('List Price/Unit'),
        'price_per_line':fields.float('List Price/Line'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'sold_for':fields.function(_sold_amount, fnct_inv=_set_sold_amount, string='Sold For', type='float',store={
                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty','misc_sale_total','misc_cost_total','price_per_line','price_per_unit'], 10),
            },),
         
        'attr_sale_price': fields.function(_cal_attr_unit_sale_price, string='Attr Sale Price', digits_compute= dp.get_precision('Account')),
        'attr_cost_price': fields.function(_cal_attr_unit_cost_price, string='Attr Cost Price', digits_compute= dp.get_precision('Account')),
        'miscellaneous_line':fields.one2many('miscellaneous.line','line_id','Miscellaneous Lines'),
        'misc_sale_total':fields.float('Misc Sale'),
        'misc_cost_total':fields.float('Misc Cost'),
        'product_cost':fields.float('Product Cost Price'),
        'price_history_id':fields.many2one('sale.price.history', 'Price History ID'),
    }
    
    def open_attributes(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'sale_attributes_form_view']], context=context)
        if ir_model_data_id:
            res_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']
        grp_ids = self._attr_grp_ids(cr, uid, [ids[0]], [], None, context)[ids[0]]
        ctx = {'open_attributes': True, 'attribute_group_ids': grp_ids}
        return {
            'name': 'Product Attributes',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': self._name,
            'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': ids and ids[0] or False,
        }

    def save_and_close_product_attributes(self, cr, uid, ids, context=None):
        self.pool.get('attribute.attribute').search(cr,uid,[('active','=',True),('model','=','sale.order.line')])
        sale_price_histroy_obj=self.pool.get('sale.price.history')
        price_history_vals={}
        attr_name=[]
        attribute_key=[]
        att_dict={}
        att_search=self.pool.get('attribute.attribute').search(cr,uid,[('active','=',True),('model','=','sale.order.line')])
#        att_search=self.pool.get('attribute.attribute').search(cr,uid,[('name','=','x_mailer_variable_data'),('model','=','sale.order.line')])
        print" ****how much data in search view",att_search
        name=self.pool.get('attribute.attribute').browse(cr,uid,att_search[0]).name
        print"name",name
        print"att_search",att_search
        if att_search:
            att_read=self.pool.get('attribute.attribute').read(cr,uid,att_search,['name','ttype'])
            print"att_read",att_read
            for each in att_read:
                if isinstance(each,dict):
                    att_dict[str(each['name'])]={'ttype':str(each['ttype']),'id':str(each['id'])}
                    attribute_key.append(str(each['name']))
        read_data=self.pool.get('sale.order.line').read(cr,uid,ids,attribute_key)
        for data in read_data:
            for each1 in attribute_key:
                if each1=='x_mailer_variable_data':
                    print" data[each1]",data[each1]
                if att_dict.has_key(each1):
                    if data[each1]:
                        cr.execute("delete from sale_price_history where order_line_id = '"+str(ids[0])+"' and attribute_id = '"+str(att_dict[each1]['id'])+"'")
                        if att_dict[each1]['ttype'] in ['many2one']:
                            option_data = self.pool.get('attribute.option').browse(cr, uid, data[each1][0])
                        elif att_dict[each1]['ttype'] in ['many2many']:
                            id_va_m2m=[x for x in att_dict[each1]]
                        else:
                            option_search_ids = self.pool.get('attribute.option').search(cr, uid, [], limit=1)
                            if option_search_ids:
                                option_data = self.pool.get('attribute.option').browse(cr, uid, option_search_ids[0])
                        if option_data:
                            price_history_vals.update(
                            {
                            'order_line_id':ids and ids[0] or False,
                            'attribute_id':str(att_dict[each1]['id']),
                            'sale_price':option_data.sales_price,
                            'cost_price':option_data.cost_price,
                            'calculation_method':option_data.price
                            }
                        )
                        sale_price_histroy_obj.create(cr,uid,price_history_vals)

        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr,uid,ids):
            order_id = line.order_id.id
            cur = line.order_id.pricelist_id.currency_id
            untaxed = 0.0
            total = 0.0
            tax = 0.0
            for all in line.order_id.order_line:
                val = 0.0
                val += self.pool.get('sale.order')._amount_line_tax(cr, uid, all, context=context)
                tax += cur_obj.round(cr, uid, cur, val)
                untaxed += all.sold_for
            total = tax + untaxed
            arg=line.order_id.amount_untaxed
            
            mod_obj = self.pool.get('ir.model.data')
            res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
            res_id = res and res[1] or False
            if arg!=line.sold_for:
                cr.execute('''update sale_order set amount_untaxed=%s,amount_tax=%s,amount_total = %s where id in %s''',(untaxed,tax,total, tuple([line.order_id.id])))
            return{
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': [res_id],
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',

                    'res_id':order_id
                    }


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
	if context.get('active_id'):
	    order_id=self.browse(cr,uid,context.get('active_id')).order_id
	    state=self.pool.get('sale.order').browse(cr,uid,order_id.id).state

        def translate_view(source):
            """Return a translation of type view of source."""
            return translate(
                cr, None, 'view', context.get('lang'), source
            ) or source

        result = super(sale_order_line, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and context.get('attribute_group_ids'):
            eview = etree.fromstring(result['arch'])
            
            #hide button under the name
            button = eview.xpath("//button[@name='open_attributes']")
            if button:
                button = button[0]
                button.getparent().remove(button)
            attributes_notebook, toupdate_fields = self.pool.get('attribute.attribute')._build_attributes_notebook(cr, uid, context['attribute_group_ids'], context=context)
            result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))
            if context.get('open_attributes'):
                placeholder = eview.xpath("//separator[@string='attributes_placeholder']")[0]
                placeholder.getparent().replace(placeholder, attributes_notebook)
            elif context.get('open_product_by_attribute_set'):
                main_page = etree.Element(
                    'page',
                    string=translate_view('Custom Attributes')
                )
                main_page.append(attributes_notebook)
                info_page = eview.xpath(
                    "//page[@string='%s']" % (translate_view('Information'),)
                )[0]
                info_page.addnext(main_page)


            result['arch'] = etree.tostring(eview, pretty_print=True)
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//notebook[@name='attributes_notebook']/page/group"):
                for new in node.xpath("//field"):
                    if state in ['review','waiting_approved_signature']:
                        new.set('readonly','True')
                        setup_modifiers(new, result['fields'])
                result['arch'] = etree.tostring(doc)
        return result
    
    def field_change(self, cr, uid, ids, field_id, context=None):
        res = {}
        res['value'] = {}
        if field_id:
            filter_ids = self.pool.get('attribute.attribute').search(cr, uid, [('domain_field_id','=',field_id)])
            if filter_ids:
                for val in self.pool.get('attribute.attribute').read(cr, uid, filter_ids, ['name']):
                    res['value'].update({str(val['name']):False})
        return res

    def copy_lines(self,cr,uid,ids,vals,context=None):
         sol_object=self.browse(cr,uid,ids)
         for each in sol_object:
            copy_line=self.copy(cr, uid,each.id,vals,context)
            sal_id_val=self.browse(cr,uid,copy_line).order_id.id
            mod_obj = self.pool.get('ir.model.data')
            res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
            res_id = res and res[1] or False
         return{
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'view_id': [res_id],
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id':sal_id_val

                }

    def write(self,cr,uid,ids,vals,context=None):

         if 'x_custom_json_attrs' not in vals.keys():
             attr_obj = self.pool.get('attribute.attribute')
             option_obj = self.pool.get('attribute.option')
             price_per_unit = 0
             price_per_order_line = 0
             so_line_obj = self.browse(cr, uid, ids[0])
             so_line_data = self.read(cr, uid, ids[0])
             attr_names = []
             so_line_attrs = {}
             if so_line_obj.attribute_set_id:
                 for each_grp_id in so_line_obj.attribute_set_id.attribute_group_ids:
                     for each_attr_id in each_grp_id.attribute_ids:
                         attr_names.append(each_attr_id.attribute_id.name)
                 for each in attr_names:
                     if each not in vals.keys():
                         if isinstance(so_line_data[each],tuple):
                             if len(so_line_data[each]):
                                 so_line_data[each] = so_line_data[each][0]
                         elif isinstance(so_line_data[each],list):
                             so_line_data[each] = [[6,False,so_line_data[each]]]
                         vals.update({each:so_line_data[each]})
                     else:
                         pass
                 for each in vals:
                     if 'x_' in each:
                         attr_id = attr_obj.search(cr, uid, [('name','=',each),('model','=','sale.order.line')])
                         if attr_id:
                             attr_data = attr_obj.read(cr, uid, attr_id[0],[])
                             if attr_data['ttype'] == 'many2one':
                                 if vals[each]:
                                     attr_option_data = option_obj.read(cr, uid, vals[each], [])

                                     if attr_option_data['price'] == 'per_unit':
                                          price_per_unit += attr_option_data['sales_price']
                                     elif attr_option_data['price'] == "based_order_lines":
                                         price_per_order_line += attr_option_data['sales_price']
                                     else:
                                         pass
                             elif attr_data['ttype'] == 'many2many':
                                 if vals[each]:
                                     if len(vals[each][0][2]):
                                         for each in vals[each][0][2]:
                                             attr_option_data = option_obj.read(cr, uid, each, [])


                                             if attr_option_data['price'] == 'per_unit':
                                                 price_per_unit += attr_option_data['sales_price']
                                             elif attr_option_data['price'] == "based_order_lines":
                                                 price_per_order_line += attr_option_data['sales_price']
                                             else:
                                                 pass
                             else:
                                 if vals[each]:
                                     attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_data['id'])])
                                     if len(attr_option_obj):
                                         attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])

                                         if attr_option_data['price'] == 'per_unit':
                                             price_per_unit += attr_option_data['sales_price']
                                         elif attr_option_data['price'] == "based_order_lines":
                                             price_per_order_line += attr_option_data['sales_price']
                                         else:
                                             pass
                         else:
                             _logger.warning("Attribute not created for sale order line.")
                 price_subtotal = so_line_data['product_uom_qty'] * price_per_unit + price_per_order_line + so_line_data['price_unit']
                 if price_per_order_line>0 and not vals.get('sold_for'):
                     vals.update({'price_per_line':price_per_order_line})
                 if price_per_unit>0 and not vals.get('sold_for'):
                     list_price=self.browse(cr,uid,ids[0]).product_id.list_price
                     vals.update({'price_unit':price_per_unit+list_price})
                     vals.update({'price_per_unit':price_per_unit})

             for id in self.browse(cr,uid,ids):
                sale_id=id.order_id.id
                if id.order_id.state=='approved':
                    print" gone to approve"
                    if id.order_id.x_signed_flag:
                        self.pool.get('sale.order').write(cr,uid,[sale_id],{'state':'draft'},context)
         res=super(sale_order_line,self).write(cr,uid,ids,vals,context)
         return res


sale_order_line()

class attribute_switch(osv.TransientModel):
    _name = 'attribute.switch'

    def default_get(self,cr, uid, fields ,context=None):
        if not context:
            context = {}
        active_ids = context.get('active_ids',[]) or []
        res = super(attribute_switch, self).default_get(cr, uid, fields, context)

        for each in self.pool.get('sale.order.line').browse(cr,uid,active_ids):
            if 'old_attribute_set_id' in fields:
                res.update({'old_attribute_set_id':each.attribute_set_id and each.attribute_set_id.id or False})
            return res

    _columns = {
                 'old_attribute_set_id':fields.many2one('attribute.set', ' Old Attribute Set',readonly=True),
                 'new_attribute_set_id':fields.many2one('attribute.set','New Attribute Set',required=True),
                }

    def save_and_close_switch(self, cr, uid, ids, context=None):
        
        active_id=context.get('active_ids')
        
        grp_ids = []
        attribute_set_id=self.browse(cr,uid,ids[0]).new_attribute_set_id.id
        
        sol_obj=self.pool.get('sale.order.line')
        sol_obj.write(cr,uid,active_id,{'attribute_set_id':attribute_set_id},context)
        new_active_id=sol_obj.search(cr,uid,[('attribute_set_id','=',attribute_set_id),('id','=',active_id[0])])
        for val in sol_obj.browse(cr, uid, active_id):
            for line in val.attribute_group_ids:
                grp_ids.append(line.id)
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'sale_attributes_form_view']], context=context)
        if ir_model_data_id:
            res_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']
        ctx = {'open_attributes': True, 'attribute_group_ids': grp_ids, 'active_id':active_id[0],'active_ids':active_id}

        return {
            'name': 'Product Attributes',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': sol_obj._name,
            'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': new_active_id and new_active_id[0] or False,
        }


class account_tax(osv.osv):
      
     _inherit = "account.tax"
     """
     A tax object.
  
     Type: percent, fixed, none, code
         PERCENT: tax = price * amount
         FIXED: tax = price + amount
         NONE: no tax line
         CODE: execute python code. localcontext = {'price_unit':pu}
             return result in the context
             Ex: result=round(price_unit*0.21,4)
     """
      
      
 #     Included a new param - price_per_order_line
     def compute_all(self, cr, uid, taxes, price_unit,  quantity, product=None, partner=None, force_excluded=False, price_misc_cost = 0,price_per_line=0):
         """
         :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
             tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
             False
         RETURN: {
                 'total': 0.0,                # Total without taxes
                 'total_included: 0.0,        # Total with taxes
                 'taxes': []                  # List of taxes, see compute for the format
             }
         """
  
         # By default, for each tax, tax amount will first be computed
         # and rounded at the 'Account' decimal precision for each
         # PO/SO/invoice line and then these rounded amounts will be
         # summed, leading to the total amount for that tax. But, if the
         # company has tax_calculation_rounding_method = round_globally,
         # we still follow the same method, but we use a much larger
         # precision when we round the tax amount for each line (we use
         # the 'Account' decimal precision + 5), and that way it's like
         # rounding after the sum of the tax amounts of each line
         precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
         tax_compute_precision = precision
         if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
             tax_compute_precision += 5
         if price_misc_cost and price_per_line:
             price_new = (price_unit + price_misc_cost+price_per_line)/quantity
             
         else:
             price_new = price_unit * quantity
         
         totalin = totalex = round(price_new, precision)
         
         tin = []
         tex = []
         
         for tax in taxes:
             if not tax.price_include or force_excluded:
                 tex.append(tax)
             else:
                 tin.append(tax)
         tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
         
         for r in tin:
             totalex -= r.get('amount', 0.0)
         totlex_qty = 0.0
         try:
             totlex_qty = totalex/quantity
         except:
             pass
         tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
         for r in tex:
             totalin += r.get('amount', 0.0)
         
         return {
             'total': totalex,
             'total_included': totalin,
             'taxes': tin + tex
         }
  
     def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
         """
         Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
         Price Unit is a Tax included price
  
         RETURN:
             [ tax ]
             tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
             one tax for each tax id in IDS and their children
         """
         if not precision:
             precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
         res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner=None)
         total = 0.0
         for r in res:
             if r.get('balance',False):
                 r['amount'] = round(r['balance'] * quantity, precision) - total
             else:
                 r['amount'] = round(r['amount'] * quantity, precision)
                 total += r['amount']
         return res
  
account_tax()


class manufacture_info(osv.osv):
    _name="manufacture.info"
    _discription="manufacturer information"

    _columns={
    'name':fields.char('Manufacturer',size=20,required=True),


    }

manufacture_info()


class franchise_info(osv.osv):
    _name="franchise.info"
    _description="franchise information"

    _columns={

    'name':fields.char('Franchise',size=20,required=True),
    'manufacture_id':fields.many2one('manufacture.info','Manufacture'),
    }
franchise_info()


class campaign_theme(osv.osv):
    _name="campaign.theme"
    _description="sale campaign"
    _columns={

    'name':fields.char('Name',size=128,required=True),
    'active':fields.boolean('Active'),

    }

    _defaults = {
                'active':True
                }
campaign_theme()


class guarantee_type(osv.osv):
    _name="guarantee.type"
    _description="guarantee type information"
    _columns={

    'name':fields.char('Name',size=128,required=True),
    'verbiage':fields.text('Guarantee Verbiage',size=1024),
    }

guarantee_type()


class coop_info(osv.osv):
    _name="coop.info"
    _description="coop type information"
    _columns={

    'name':fields.char('Name',size=128,required=True),
    }

coop_info()



class sale_price_history(osv.osv):
    _name="sale.price.history"
    _columns={
    'order_line_id':fields.many2one('sale.order.line','Order Line'),
    'attribute_id':fields.many2one('attribute.attribute','Attribute'),
    'sale_price':fields.float('Sale price'),
    'cost_price':fields.float('Cost price'),
    'calculation_method':fields.selection([('per_unit','Per Unit'),('based_order_lines','Per Order Line')],'Calculation Method'),
    'sale_price_wizard_id':fields.many2one('sale.price.history.wizard','Sale Price History')
    }
sale_price_history()

class account_invoice_line(osv.osv):
    _inherit="account.invoice.line"
    _description=" Selction of Sales order lines"

    _columns={

    'sale_order_line_id':fields.many2one('sale.order.line','Order line'),
    }
account_invoice_line()
   
class miscellaneous_items(osv.osv):
    _name = 'miscellaneous.items'
    
    _columns = {
                'name':fields.char('Miscellaneous Item',sizre=64,required=True),
                'sales_price':fields.float('Sales Price',digits=(16,2),required=True),
                'cost_price':fields.float('Cost Price',digits=(16,2),required=True),
                }

class miscellaneous_line(osv.osv):
    _name = 'miscellaneous.line'

    def onchange_miscellaneous_id(self,cr, uid, ids, miscellaneous, context=None):
        v = {}
        if miscellaneous:
            item = self.pool.get('miscellaneous.items').browse(cr,uid,miscellaneous)
            if cost_price:
                v['misc_cost_price'] = item.cost_price
            if sale_price:
                v['misc_sales_price'] = item.sales_price
        return {'value': v}

    _columns = {
                'miscellaneous_id':fields.many2one('miscellaneous.items','Miscellaneous Items',required=True),
                'line_id':fields.many2one('sale.order.line','Sale Order Line'),
                'misc_cost_price':fields.float('Cost Price',digits=(16,2),required=True),
                'misc_sales_price':fields.float('Sales Price',digits=(16,2),required=True),
                }
    
    _sql_constraints = [('unique_item','unique(line_id,miscellaneous_id)','Unable to add same Miscellaneous Item twice.')]


miscellaneous_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns={
    'sale_order_id':fields.many2one('sale.order','Quotation'),
    }
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns={
    'x_version_no':fields.char('V',size=10),
    'x_drop_no':fields.char('D',size=10),

    }

