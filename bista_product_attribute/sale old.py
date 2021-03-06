from datetime import datetime, timedelta
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
    _inherit = "sale.order"

    def add_product_order_line(self,cr,uid,ids,context=None):
            read_data={}
            vals={}
            sales_price=0
            sales_price_per_unit = 0
            sales_price_per_order_line = 0
            sale_data=self.browse(cr,uid,ids[0])

            attr_name_in_product=[]
            attr_type_in_product=[]

    #        attr_name_type_dict = {}

            if sale_data.add_product_id.attribute_set_id:
                attribute_set_val=sale_data.add_product_id.attribute_set_id.attribute_group_ids
                print "attribute_set_val",attribute_set_val
                for each in attribute_set_val:
                    for y in each.attribute_ids:
        #                attr_name_type_dict[str(y.attribute_type)] = str(y.name)
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_type)





                read_data=self.pool.get('product.product').read(cr,uid,[sale_data.add_product_id.id],attr_name_in_product)
                read_data = read_data[0]



            print"read value got",read_data

            if sale_data.add_product_id:
                vals.update({'product_id':sale_data.add_product_id.id,
                'order_id':sale_data.id,
                'name':sale_data.add_product_id.name,
                'attribute_set_id':sale_data.add_product_id.attribute_set_id and sale_data.add_product_id.attribute_set_id.id or False,
                })

                for each in read_data:
                    if each in attr_name_in_product:
                        i = attr_name_in_product.index(each)

                        if attr_type_in_product[i] == 'select':
                            print "select type attribute"
                            print read_data[each]
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

#                                 sales_price += sales_price_select
                                print read_data[each]

                        elif attr_type_in_product[i] == 'multiselect':
                            print "multiselect type attribute"
                            print read_data[each]
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

#                                     sales_price += sales_price_multi
                                read_data[each] = [(6,0,read_data[each])]

                                print [(6,0,read_data[each])]
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
                            
#                             sales_price += sales_price_other
                sales_price = self.pool.get('product.product').browse(cr,uid,sale_data.add_product_id.id).list_price
                vals.update(read_data)

                vals.update({'price_unit':sales_price,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})


                print "===============vals=========",vals
                
                print "===============Sale price-------------", vals['price_unit']
                print "===============sales_price_per_order_line-------------", vals['price_per_line']
                print "===============sales_price_per_unit-------------", vals['price_per_unit']

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

    #        attr_name_type_dict = {}


            if sale_data.add_product_temp_id.attribute_id:
                attribute_set_val=sale_data.add_product_temp_id.attribute_id.attribute_group_ids
                for each in attribute_set_val:
                    for y in each.attribute_ids:
        #
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_type)
        #

            read_data=self.pool.get('base.product.template').read(cr,uid,[sale_data.add_product_temp_id.id],attr_name_in_product)
            read_data = read_data[0]



            print"read value got===",read_data
    #        print attribute_vals

            if sale_data.add_product_temp_id:
                vals.update({'product_id':sale_data.add_product_temp_id.product_id.id,
                'order_id':sale_data.id,
                'name':sale_data.add_product_temp_id.name,
                'attribute_set_id':sale_data.add_product_temp_id.attribute_id and sale_data.add_product_temp_id.attribute_id.id or False,
    #
                })

                for each in read_data:
                    if each in attr_name_in_product:
                        i = attr_name_in_product.index(each)
                        if attr_type_in_product[i] == 'select':
                            print "select type attribute"
                            print read_data[each]
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

#                                 sales_price += sales_price_select
                                print"sales_price"

                                print read_data[each]
                            else:
                                pass

                        elif attr_type_in_product[i] == 'multiselect':
                            if read_data[each]:

                                print read_data[each]

                                for each_attr_id in read_data[each]:
                                    sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price
                                    calculation_method = self.pool.get('attribute.option').browse(cr,uid,each_attr_id).price
                                    if calculation_method == "per_unit":
                                        sales_price_per_unit += sales_price_multi
                                    elif calculation_method == "based_order_lines":
                                        sales_price_per_order_line += sales_price_multi
                                    else:
                                        pass

#                                     sales_price += sales_price_multi

                                read_data[each] = [(6,0,read_data[each])]
                                print [(6,0,read_data[each])]
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
                            
#                             sales_price += sales_price_other
#                 sales_price = self.pool.get('product.product').browse(cr,uid,sale_data.add_product_id.id).list_price
#                             sales_price += sales_price_other

                sales_price = self.pool.get('product.product').browse(cr,uid,sale_data.add_product_temp_id.product_id.id).list_price
                vals.update(read_data)
#                 vals.update({'price_unit':sales_price})
                vals.update({'price_unit':sales_price,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})


                print "Final Product Vals for template : " ,vals
                vals.pop('id')
                print"vals after id ",vals
                sol_id = self.pool.get('sale.order.line').create(cr,uid,vals)

                print"gor id for line",sol_id

#                sale_order_line_data = self.pool.get('sale.order.line').read(cr, uid, sol_id,[])

    #            print "sale_order_line_data ",sale_order_line_data

                self.write(cr,uid,ids,{'add_product_temp_id':False})


            return True
        except:
            pass

    def add_bundle_order_line(self,cr,uid,ids,context=None):

#         try:
#             vals={}
            sale_data=self.browse(cr,uid,ids[0])

            print sale_data.add_product_bundle_id.template_id

            for each_template in sale_data.add_product_bundle_id.template_id:

                vals={}
                attr_name_in_product=[]
                attr_type_in_product=[]
                sales_price=0
                sales_price_per_unit = 0
                sales_price_per_order_line = 0

                print"template_id",each_template
                attribute_set_val=each_template.attribute_id.attribute_group_ids
                print "attribute_group_ids",attribute_set_val
                for each in attribute_set_val:
                    for y in each.attribute_ids:
        #
                        attr_name_in_product.append(y.name)
                        attr_type_in_product.append(y.attribute_type)
    #

                print "attr_name_in_product",attr_name_in_product
                print "attr_type_in_product",attr_type_in_product


                read_data=self.pool.get('base.product.template').read(cr,uid,[each_template.id],attr_name_in_product)
                read_data = read_data[0]
                print"read data value:",read_data



#                 template_ids_val=sale_data.add_product_bundle_id.template_id
                
                template_ids_val = each_template.id
                print"total template ids got",template_ids_val


<<<<<<< .mine
                if sale_data.add_product_bundle_id:
                        for each in template_ids_val:
                            print"each ka value",each
                            vals.update({'product_id':each.product_id.id,
                            'order_id':sale_data.id,
                            'name':each.name,
                            'attribute_set_id':each.attribute_id and each.attribute_id.id or False
=======
#                 if sale_data.add_product_bundle_id:
#                     for each in template_ids_val:
#                         print"each ka value",each
                print "Vals------------",vals
                vals.update({'product_id':each_template.product_id.id,
                'order_id':sale_data.id,
                'name':each_template.name,
                'attribute_set_id':each_template.attribute_id and each_template.attribute_id.id or False

                            })
                            print"vals value second time",vals
                            for each1 in read_data:
                                print"second time read time",each1
                                if each1 in attr_name_in_product:
                                    i = attr_name_in_product.index(each1)
                                    if attr_type_in_product[i] == 'select':
=
                })
                print vals
                for each1 in read_data:
                    print "Each1------------", each1,attr_name_in_product
                    if each1 in attr_name_in_product:
                        i = attr_name_in_product.index(each1)
                        print i
                        if attr_type_in_product[i] == 'select':
                            print attr_type_in_product[i]
                            print " select----------", read_data[each1]

                                        print read_data[each1]
                                        if read_data[each1]:
                                            read_data[each1] = read_data[each1][0]
                                            sales_price_select=self.pool.get('attribute.option').browse(cr,uid,read_data[each1]).sales_price

                            print read_data[each1]
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
>>>>>>> .r730

<<<<<<< .mine
                                            sales_price += sales_price_select
                                            print read_data[each1]
                                        else:
                                            pass

                                    elif attr_type_in_product[i] == 'multiselect':


                                        print read_data[each1]
                                        if read_data[each1]:
                                            for each_attr_id in read_data[each1]:
                                                sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price

                                print read_data[each1]
                            else:
                                pass
>>>>>>> .r730

<<<<<<< .mine
                                                sales_price += sales_price_multi
                                            read_data[each1] = [(6,0,read_data[each1])]
                                            print [(6,0,read_data[each1])]
                                        else:
                                            read_data[each1] = False
=======
                        elif attr_type_in_product[i] == 'multiselect':
>>>>>>> .r730

                            print " multiselect----------", read_data[each1]
                            print attr_type_in_product[i]
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

<<<<<<< .mine
                                    else:
                                        search_id=self.pool.get('attribute.attribute').search(cr,uid,[('model','=','product.product'),('name','=',each1)])
=======
#                                         sales_price += sales_price_multi
                                read_data[each1] = [(6,0,read_data[each1])]
                                print [(6,0,read_data[each1])]
                            else:
                                read_data[each1] = [(6,0,[])]
                        else:
                            print attr_type_in_product[i]
                            search_id = self.pool.get('attribute.attribute').search(cr,uid,[('model','=','product.product'),('name','=',each1)])
                            print "search id ",search_id
#                             try:
                            sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
                            calculation_method = self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].price
                            
                            print calculation_method
                            if read_data[each1]:
                                if calculation_method == "per_unit":
                                    sales_price_per_unit += sales_price_other
                                elif calculation_method == "based_order_lines":
                                    sales_price_per_order_line += sales_price_other
                                else:
                                    pass
#                             except:
#                                 pass
>>>>>>> .r730

<<<<<<< .mine
                                        sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price
=======
#                                 sales_price += sales_price_other
#                     for list_price_val in each_template:
                sales_price = self.pool.get('product.product').browse(cr,uid,each_template.product_id.id).list_price
                vals.update(read_data)
                vals.update({'price_unit':sales_price,'price_per_line':sales_price_per_order_line,'price_per_unit':sales_price_per_unit})
#                     vals.update({'price_unit':sales_price})
                print "Final Product Vals : " ,vals
                vals.pop('id')
                self.pool.get('sale.order.line').create(cr,uid,vals)
                self.write(cr,uid,ids,{'add_product_bundle_id':False})
>>>>>>> .r730

<<<<<<< .mine
                                        sales_price += sales_price_other
    #                            for list_price_val in template_ids_val:
    #                                sales_price += self.pool.get('product.product').browse(cr,uid,list_price_val.product_id.id).list_price
    #                                vals.update(read_data)
    #                                vals.update({'price_unit':sales_price})
                            print "Final Product Vals : " ,vals
                            sol_id=self.pool.get('sale.order.line').create(cr,uid,vals)
=======
>>>>>>> .r730

<<<<<<< .mine
                            print" check karo sol kitne bhi bar",sol_id
                            self.write(cr,uid,ids,{'add_product_bundle_id':False})

=======
>>>>>>> .r730

<<<<<<< .mine
        

        except:
            pass
=======
#         except:
#             pass
>>>>>>> .r730


#    def _get_default_manger_id(self,cr,uid,context=None):
#
#            admin_id_def=self.pool.get('res.users').search(cr,uid,[('name','=','Administrator')])
#            return admin_id_def and admin_id_def[0] or False
#
#    def _get_default_company_id(self,cr,uid,context=None):
#
#            company_id_def=self.pool.get('res.partner').search(cr,uid,[('x_is_billing_vendor','=',True)])
#            return company_id_def and company_id_def[0] or False
#
#
#    def _get_default_contact_id(self,cr,uid,context=None):
#
#            contact_id_def=self.pool.get('res.partner').search(cr,uid,[('x_is_billing_vendor','=',True)])
#            return contact_id_def and contact_id_def[0] or False



    def onchange_manufacture_id(self, cr, uid, ids, x_manufacturer, context=None):
       v = {}

       v['x_franchise']=False

       return {'value': v}


    def onchange_guarantee_type_id(self, cr, uid, ids, x_guarantee_type_id, context=None):
       v = {}

       print "ids value",ids
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
            print"res value ",res

            if self.pool.get('res.partner').browse(cr,uid,part).is_company:
                res['value'].update({'x_signing_company_id':part})
#            warn_msg = _('Customer is not a Company')
#            warning = {
#                       'title': _('Alert!'),
#                       'message' : warn_msg
#
#                    }
#            res.update({'warning':warning})
            else:

                res['value'].update({'x_signing_company_id':False})
        return res









    _columns = {
#        'product_temp_id':fields.many2one('product.template','Product Template'),
        'add_product_id':fields.many2one('product.product','Product',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
        'add_product_temp_id':fields.many2one('base.product.template','Product Template',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'add_product_bundle_id':fields.many2one('base.product.bundle','Product Bundle',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_billing_vendor_id':fields.many2one('res.partner','Billing Vendor',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_manager_id':fields.many2one('res.users','Sales Manager',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_cs_rep_id':fields.many2one('res.users','Client Service Rep',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]},),
        'x_billing_month':fields.selection([('jan','January'),('feb','February'),('mar','March'),('apr','April'),('may','May'),('june','June'),('july','July'),('aug','August'),('sep','September'),('oct','October'),('nov','November'),('dec','December')],'Billing Month',states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),
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
        'x_payment_due_date':fields.date('Payment Date',required=True,states={'review': [('readonly', True)], 'waiting_approved_signature': [('readonly', True)]}),


    }

    _defaults={
#    'x_manager_id':_get_default_manger_id,
#    'x_signing_company_id':_get_default_company_id,
#
#    'x_billing_vendor_id':_get_default_contact_id,
    

   }



    def create(self, cr, uid, vals, context=None):


        current_year=datetime.now().year
        print"got current year",current_year
        if vals.get('x_billing_year')!=current_year:
            raise osv.except_osv(_('Error!'),
                _('Year in not valid'))


        res=super(sale_order, self).create(cr, uid, vals, context=context)
        return res

#    def write(self,cr,uid,ids,vals,context=None):
#        res = super(sale_order,self).write(cr,uid,ids,vals,context)
#        attr_name=[]
#        for each in self.browse(cr,uid,ids):
#            for line in each.order_line:
#                if line.attribute_set_id:
#                    for attribute_group in line.attribute_set_id.attribute_group_ids:
#                        for attribute in attribute_group.attribute_ids:
#                            print"<===============================>",attribute.name
#                            if attribute.required_on_views:
#                                attr_name.append(attribute.name)
#
#
#                            print"required wala field mil gaya== list me===>",attr_name
#                    for each_line in self.pool.get('sale.order.line').read(cr,uid,[line.id],attr_name):
#                        print"dictionary value",each
#                        for value in each_line:
#                            if not each_line.get(value):
#                                raise osv.except_osv(_('Error!'), _('Attribute \n %s')%(value+  ' is missing'))
#
#        return res

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
        price_per_order_line = 0
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price_per_order_line = line.price_per_line * (1 - (line.discount or 0.0) / 100.0)
#             Add the Attributs price which are defined to be calculated on per unit of product
            price = (line.price_unit + line.price_per_unit) * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id, price_per_order_line)
            print "=============taxes========",taxes
            taxes['total'] = taxes['total'] + price_per_order_line
            taxes['total_included'] = taxes['total_included'] + price_per_order_line
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'attribute_group_ids': fields.function(_attr_grp_ids, type='many2many',
        relation='attribute.group', string='Groups'),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'price_per_unit':fields.float('List Price/Unit'),
        'price_per_line':fields.float('List Price/Line'),
<<<<<<< .mine
        'product_uom_qty': fields.integer('Quantity', required=True, readonly=True, states={'draft': [('readonly', False)]}),

=======
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
>>>>>>> .r730
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
        return {'type': 'ir.actions.act_window_close'}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

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
        return result


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,
            context=None):



                result= super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty,
                uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order, packaging
                , fiscal_position, flag, context)

                if product:
                    print"result value",result
                    read_data={}

                    sales_price=0
                    attr_name_in_product=[]
                    attr_type_in_product=[]
                    try:
                        attribute_set_val=self.pool.get('product.product').browse(cr,uid,product).attribute_set_id.attribute_group_ids
                        for each in attribute_set_val:
                            for y in each.attribute_ids:
                #                attr_name_type_dict[str(y.attribute_type)] = str(y.name)
                                attr_name_in_product.append(y.name)
                                attr_type_in_product.append(y.attribute_type)

                        read_data=self.pool.get('product.product').read(cr,uid,[product],attr_name_in_product)
                        read_data = read_data[0]

                        print"read value got",read_data

                        for each in read_data:
                            if each in attr_name_in_product:
                                i = attr_name_in_product.index(each)
                                if attr_type_in_product[i] == 'select':
                                    print "select type attribute"
                                    print read_data[each]
                                    read_data[each] = read_data[each][0]
                                    sales_price_select=self.pool.get('attribute.option').browse(cr,uid,read_data[each]).sales_price

                                    sales_price += sales_price_select
                                    print read_data[each]

                                elif attr_type_in_product[i] == 'multiselect':
                                    print "multiselect type attribute"
                                    print read_data[each]
                                    for each_attr_id in read_data[each]:
                                        sales_price_multi= self.pool.get('attribute.option').browse(cr,uid,each_attr_id).sales_price

                                        sales_price += sales_price_multi
                                    read_data[each] = [(6,0,read_data[each])]

                                    print [(6,0,read_data[each])]

                                else:
                                    search_id=self.pool.get('attribute.attribute').search(cr,uid,[('model','=','product.product'),('name','=',each)])
                                    sales_price_other= self.pool.get('attribute.attribute').browse(cr,uid,search_id[0]).option_ids[0].sales_price

                                    sales_price += sales_price_other
                        price_unit_toatal=sales_price+self.pool.get('product.product').browse(cr,uid,product).list_price
                        print"final price=========",price_unit_toatal



                        result['value'].update({'price_unit':price_unit_toatal})

                        return result
                    except:
                        _logger.warning('attribute set not mentioned')


                return result



    def copy_lines(self,cr,uid,ids,vals,context=None):


         sol_object=self.browse(cr,uid,ids)
         for each in sol_object:

            copy_line=self.copy(cr, uid,each.id,vals,context)
            print"==========",copy_line
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
<<<<<<< .mine

=======
         
    def write(self,cr,uid,ids,vals,context=None):
        
        if 'x_custom_json_attrs' not in vals.keys():
            print "write vals", vals
            attr_obj = self.pool.get('attribute.attribute')
            option_obj = self.pool.get('attribute.option')
            price_per_unit = 0
            price_per_order_line = 0
            so_line_obj = self.browse(cr, uid, ids[0])
            so_line_data = self.read(cr, uid, ids[0])
            print "so_line_data", so_line_data
            attr_names = []
            so_line_attrs = {}
            for each_grp_id in so_line_obj.attribute_set_id.attribute_group_ids:
                for each_attr_id in each_grp_id.attribute_ids:
                    attr_names.append(each_attr_id.name)
            print "attr_names", attr_names 
            
    #         for each in attr_names:
    #             if each in so_line_data.keys():
    #                 if each in vals.keys():
    #                     so_line_attrs.update({each:vals[each]})
    #                 so_line_attrs.update({each:so_line_data[each]})
    #                 so_line_keys[each] 
            for each in attr_names:
                if each not in vals.keys():
                    if isinstance(so_line_data[each],tuple):
                        if len(so_line_data[each]):
                            so_line_data[each] = so_line_data[each][0]
#                     elif isinstance(so_line_data[each],list) and len(so_line_data[each]):
                    elif isinstance(so_line_data[each],list):
                        print "Multiselect ", so_line_data[each]
                        so_line_data[each] = [[6,False,so_line_data[each]]]
                    vals.update({each:so_line_data[each]})
                else: 
                    pass    
    #                 so_line_attrs.update({each:so_line_data[each]})
    
                    
            print "Attributes need to be calculated", vals
               
            for each in vals:
                if 'x_' in each:
                    attr_id = attr_obj.search(cr, uid, [('name','=',each),('model','=','sale.order.line')])
                    if attr_id:
                        attr_data = attr_obj.read(cr, uid, attr_id[0],[])
                        if attr_data['ttype'] == 'many2one':
                            if vals[each]:
    #                             attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_data['id']), ('name','=',vals[each])])
    #                             print "attr_option_obj",attr_option_obj
                                print "Many2One DAta"
                                print vals[each]
                                attr_option_data = option_obj.read(cr, uid, vals[each], [])
                                print "attr_option_data", attr_option_data
                                if attr_option_data['price'] == 'per_unit':
                                    price_per_unit += attr_option_data['sales_price']
                                elif attr_option_data['price'] == "based_order_lines":
                                    price_per_order_line += attr_option_data['sales_price']
                                else:
                                    pass
                        elif attr_data['ttype'] == 'many2many':
                            if vals[each]:
                                print "many2many data"
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
                            print "other fields data"
                            if vals[each]:
                                attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_data['id'])])
                                if len(attr_option_obj):
        #                             If Attribute type is not relational than search in the attribute options with attr ID and taken the first Attribute option id.
                                    attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])
                                    print "attr_option_data", attr_option_data
                                    if attr_option_data['price'] == 'per_unit':
                                        price_per_unit += attr_option_data['sales_price']
                                    elif attr_option_data['price'] == "based_order_lines":
                                        price_per_order_line += attr_option_data['sales_price']
                                    else:
                                        pass
                                
                    else:
                        _logger.warning("Attribute not created for sale order line.")
    #                 print attr_id
    #                 attr_option_id = self.pool.get('attribute.option').search(cr, uid, [('attribute_id','=',attr_id[0]), ('name','=',vals[each])])
    #                 if attr_option_id:
    #                     attr_option_obj = option_obj.read(cr, uid, attr_option_id[0])
    #                     print "attr_option_obj ",attr_option_obj
    # #                 if attr_id:
    #                     attr_data = attr_obj.browse(cr, uid, attr_id[0])
    #                     print attr_data.option_ids
            
            print "price_per_order_line,price_per_unit", price_per_order_line,price_per_unit
            
            price_subtotal = so_line_data['product_uom_qty'] * price_per_unit + price_per_order_line + so_line_data['price_unit']
            print "price_subtotal", price_subtotal
            vals.update({'price_per_line':price_per_order_line,'price_per_unit':price_per_unit,'price_subtotal':price_subtotal})
        res=super(sale_order_line,self).write(cr,uid,ids,vals,context)
        return res






#     def write(self,cr,uid,ids,vals,context=None):
#         
#         
#         
#         res=super(sale_order_line,self).write(cr,uid,ids,vals,context)
#         
#         
#         print"callind write==========,,,,,,,,==>",res
# 
#         attr_name=[]
#         attribute_key=[]
#         att_dict={}
#         sales_price_per_unit=0
#         sales_price_per_line=0
# 
#         att_search=self.pool.get('attribute.attribute').search(cr,uid,[('active','=',True),('model','=','sale.order.line')])
#         print"========================= got attribute id",att_search
#         if att_search:
#             att_read=self.pool.get('attribute.attribute').read(cr,uid,att_search,['name','ttype'])
#             print"========================= att_read",att_read
#             for each in att_read:
#                 if isinstance(each,dict):
#                     att_dict[str(each['name'])]={'ttype':str(each['ttype']),'id':str(each['id'])}
#                     attribute_key.append(str(each['name']))
# 
#             read_data = self.pool.get('sale.order.line').read(cr,uid,ids,attribute_key)
#             print"read_data_value================",read_data
#             for data in read_data:
#                 for each1 in attribute_key:
# 
#                     print"============each one value is",each1
#                     if att_dict.has_key(each1):
#                         if data[each1] and att_dict[each1]['ttype'] =='many2one':
#                             opt_obj=self.pool.get('attribute.option').browse(cr,uid,data[each1][0])
#                             if opt_obj.price == "per_unit":
#                                 sales_price_per_unit += opt_obj.sales_price
# 
#                             if opt_obj.price == "based_order_lines":
#                                 sales_price_per_line += opt_obj.sales_price
# 
#                         elif data[each1] and att_dict[each1]['ttype'] =='many2many':
#                             for x in data[each1]:
# 
#                                 opt_obj=self.pool.get('attribute.option').browse(cr,uid,x)
#                                 if opt_obj.price == "per_unit":
#                                     sales_price_per_unit += opt_obj.sales_price
# 
#                                 if opt_obj.price == "based_order_lines":
#                                     sales_price_per_line += opt_obj.sales_price
#                         else:
#                             if data[each1]:
#                                 attribute_obj=self.pool.get('attribute.attribute')
#                                 attribute_obj_id=attribute_obj.search(cr,uid,[('name','=',each1),('model','=','sale.order.line')])
#                                 option_ids_browse=attribute_obj.browse(cr,uid,attribute_obj_id[0]).option_ids[0]
# 
#                                 if option_ids_browse.price=="per_unit":
#                                     sales_price_per_unit +=option_ids_browse.sales_price
#                                     print"<===============sales_price_per_unit==",sales_price_per_unit
#                                 if option_ids_browse.price == "based_order_lines":
#                                     sales_price_per_line += option_ids_browse.sales_price
#                                     print"======sales_price_per_line=",sales_price_per_line
# 
# 
# 
# 
# 
#                                 print"attribute_obj_id =========vakue=========>",attribute_obj_id
#                                 print"data [each1] value ====is",data[each1]
# 
# 
#         print"<===============finalsales_price_per_unit==",sales_price_per_unit
#         print"<final===============>sales price per lines==========",sales_price_per_line
# 
# 
# 
# #                            if data[each1]:
# #                                print "====att_dict[each1]['id']====",att_dict[each1]
# #                                cr.execute("select sales_price, price from attribute_option where attribute_id = '"+str(att_dict[each1]['id'])+"' limit 1")
# #                                temp = cr.fetchone()
# #                                if temp and len(temp)>1:
# #                                    if temp[1] == "per_unit":
# #                                        sales_price_per_unit += temp[0]
# #                                    if temp[1] == "based_order_lines":
# #                                        sales_price_per_line += temp[0]
# #
# #                                    print "===sales_price_per_unit=======",temp,temp[0]
# #        for value in self.browse(cr,uid,ids):
# #            if sales_price_per_unit <> 0 or sales_price_per_line <> 0:
# #                cr.execute("update sale_order_line set price_per_unit = '"+str(sales_price_per_unit)+"', price_per_line = '"+str(sales_price_per_line)+"' where id = '"+str(ids[0])+"'")
# 
#         return res





>>>>>>> .r730
sale_order_line()

# class account_tax(osv.osv):
#      
#     _inherit = "account.tax"
#     """
#     A tax object.
#  
#     Type: percent, fixed, none, code
#         PERCENT: tax = price * amount
#         FIXED: tax = price + amount
#         NONE: no tax line
#         CODE: execute python code. localcontext = {'price_unit':pu}
#             return result in the context
#             Ex: result=round(price_unit*0.21,4)
#     """
#      
#      
# #     Included a new param - price_per_order_line
#     def compute_all(self, cr, uid, taxes, price_unit,  quantity, product=None, partner=None, force_excluded=False, price_per_order_line = 0):
#         """
#         :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
#             tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
#             False
#         RETURN: {
#                 'total': 0.0,                # Total without taxes
#                 'total_included: 0.0,        # Total with taxes
#                 'taxes': []                  # List of taxes, see compute for the format
#             }
#         """
#  
#         # By default, for each tax, tax amount will first be computed
#         # and rounded at the 'Account' decimal precision for each
#         # PO/SO/invoice line and then these rounded amounts will be
#         # summed, leading to the total amount for that tax. But, if the
#         # company has tax_calculation_rounding_method = round_globally,
#         # we still follow the same method, but we use a much larger
#         # precision when we round the tax amount for each line (we use
#         # the 'Account' decimal precision + 5), and that way it's like
#         # rounding after the sum of the tax amounts of each line
#         precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
#         tax_compute_precision = precision
#         if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
#             tax_compute_precision += 5
#         if price_per_order_line:
#             price_new = (price_unit * quantity) + price_per_order_line
#         else:
#             price_new = price_unit * quantity
#             
#         totalin = totalex = round(price_new, precision)
#         tin = []
#         tex = []
#         for tax in taxes:
#             if not tax.price_include or force_excluded:
#                 tex.append(tax)
#             else:
#                 tin.append(tax)
#         tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
#         for r in tin:
#             totalex -= r.get('amount', 0.0)
#         totlex_qty = 0.0
#         try:
#             totlex_qty = totalex/quantity
#         except:
#             pass
#         tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
#         for r in tex:
#             totalin += r.get('amount', 0.0)
#         return {
#             'total': totalex,
#             'total_included': totalin,
#             'taxes': tin + tex
#         }
#  
#     def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
#         """
#         Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
#         Price Unit is a Tax included price
#  
#         RETURN:
#             [ tax ]
#             tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
#             one tax for each tax id in IDS and their children
#         """
#         if not precision:
#             precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
#         res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner=None)
#         total = 0.0
#         for r in res:
#             if r.get('balance',False):
#                 r['amount'] = round(r['balance'] * quantity, precision) - total
#             else:
#                 r['amount'] = round(r['amount'] * quantity, precision)
#                 total += r['amount']
#         return res
#  
#  
# account_tax()


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



