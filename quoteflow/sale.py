from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class sale_order(osv.osv):
    _inherit='sale.order'
    _description='Quotation Flow'

    def print_direct_report(self,cr,uid,ids,context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        global name
        state_condt=self.browse(cr,uid,ids[0]).state
        if state_condt=='approved':
            name="quotation.sale.order2"
        else:
            name="quotation.sale.order"
        datas={'ids': ids,}
        return {
                'type': 'ir.actions.report.xml',
                'report_name': name,
                'datas': datas,
                }

    def create_invoice(self,cr,uid,ids,context=None):
        invoice_obj=self.pool.get('account.invoice')
        sale_order_line_obj=self.browse(cr,uid,ids)
        product_categ_account=0
        for each in sale_order_line_obj:
            sale_team_id=self.pool.get('crm.case.section').search(cr,uid,[('member_ids','in',each.user_id.id)])
            if not sale_team_id:
                raise osv.except_osv(_('Error!'), _('\n Sales Person %s is not associated with any Sales Team')%(each.user_id.name))
            vals={}
            if each.x_billing_vendor_id.customer and each.x_billing_vendor_id.supplier:
                account = each.x_billing_vendor_id.property_account_receivable.id
            else:
                account = each.partner_id.property_account_receivable.id
            vals.update({
            'partner_id':each.partner_id.id,
            'date_invoice':each.date_order,
            'account_id':account,
            'origin':each.name
            })
            sale_create_id=invoice_obj.create(cr,uid,vals,context=None)
            for x in each.order_line:
                    for account_lines in x.product_id.categ_id.account_lines_ids:
                        sales_team=account_lines.sales_team_id.member_ids
                        sales_person_name=[user.name for user in sales_team]
                        if each.user_id.name in sales_person_name:
                            product_categ_account = account_lines.income_account_id and account_lines.income_account_id.id
                        else:
                            raise osv.except_osv(_('Error!'), _('\n Sales Team: "%s" \n does not have member: "%s" for the Product: "%s" and Product Category: "%s" \n no Incone Account is not define')%(account_lines.sales_team_id.name,each.user_id.name,x.product_id.name,x.product_id.categ_id.name))
                    if product_categ_account==0:
                        raise osv.except_osv(_('Error!'), _('Account not defined for the Selected Product Category'))
                    list_l= [y.id for y in x.tax_id]
                    product_get=x.product_id
                    line_vals={
                    'product_id':product_get.id,
                    'name':x.name,
                    'quantity':x.product_uom_qty,
                    'invoice_id':sale_create_id,
                    'price_unit':x.price_unit,
                    'date_planned':each.date_order,
                    'invoice_line_tax_id':[(6, 0, list_l)],
                    'price_unit':x.price_unit,
                    'sale_order_line_id':x.id,
                    'account_id':product_categ_account
                        }
                    self.pool.get('account.invoice.line').create(cr,uid,line_vals,context=None)
            self.write(cr,uid,[each.id],{'state':'approved','x_signed_flag':True,'old_price_total':each.amount_total})
            self._create_purchase_order(cr,uid,ids,context)
            new_group_ids=self.pool.get('res.groups').search(cr,uid,[('notify_email','in',['notify_account','notify_manager','notify_both'])])
            for follower_id in self.pool.get('res.groups').browse(cr,uid,new_group_ids):
                    for users in follower_id.users:
                        if users.email and users.partner_id.email:
                            mail_mail = self.pool.get('mail.mail')
                            # the invite wizard should create a private message not related to any object -> no model, no res_id
                            mail_id = mail_mail.create(cr, uid, {
                                'model': 'sale.order',
                                'res_id': each.id,
                                'subject': _('Modification in Quotation # %s') % (each.name,),
                                'body_html': 'This is to notify that Total Amount for %s Quotation is changed' % (each.name,),
                                'auto_delete': True,
                                }, context=context)
                            mail_mail.send(cr, uid, [mail_id], recipient_ids=[users.partner_id.id], context=context)
            return True


    def _create_purchase_order(self,cr,uid,ids,context=None):
        dict_group_vendor={}
        dict_vendor={}
        po_dict={}
        sol_obj=self.pool.get('sale.order.line')
        po_line_dict={}
        price_per_unit=0
        po_obj=self.pool.get('purchase.order')
        pol_obj=self.pool.get('purchase.order.line')
        attr_obj=self.pool.get('attribute.attribute')
        option_obj=self.pool.get('attribute.option')
        for order in  self.browse(cr,uid,ids):
            for line in order.order_line:
                dict_vendor = {}
                dict_group_vendor = {}
                if line.attribute_set_id:
                    for attrs_grps in line.attribute_set_id.attribute_group_ids:
                        for attrs in attrs_grps.attribute_ids:
                            if attrs.vendor_id and attrs.vendor_group:
                                if dict_group_vendor.has_key(str(attrs.vendor_group)):
                                    dict_group_vendor[str(attrs.vendor_group)]['attr_ids'].append(str(attrs.attribute_id.name))
                                else:
                                    dict_group_vendor[str(attrs.vendor_group)]={'vendor_id':attrs.vendor_id.id,'attr_ids':[str(attrs.attribute_id.name)]}
                            if attrs.vendor_id and not attrs.vendor_group:
                                if dict_vendor.has_key(str(attrs.vendor_id.name)):
                                    dict_vendor[str(attrs.vendor_id.name)]['attr_ids'].append(str(attrs.attribute_id.name))
                                else:
                                    dict_vendor[str(attrs.vendor_id.name)]={'vendor_id':attrs.vendor_id.id,'attr_ids':[str(attrs.attribute_id.name)]}
                    if dict_group_vendor:
                        for key,value in dict_group_vendor.iteritems():
                            if len(dict_group_vendor[key]['attr_ids'])>0:
                                read_val=sol_obj.read(cr,uid,[line.id],dict_group_vendor[key]['attr_ids'])[0]
                                read_val.pop('id')
                                for value in read_val:
                                    if read_val.get(value):
                                        if isinstance(read_val[value],tuple):
                                            if len(read_val[value]):
                                                attr_option_data = option_obj.read(cr, uid, read_val[value][0], [])
                                                if attr_option_data['price'] == 'per_unit':
                                                    price_per_unit += attr_option_data['cost_price']
                                        elif isinstance(read_val[value],list):
                                            for attr_option_data in option_obj.read(cr, uid, read_val[value], []):
                                                if attr_option_data['price'] == 'per_unit':
                                                    price_per_unit += attr_option_data['cost_price']
                                        else:
                                            attr_id = attr_obj.search(cr, uid, [('name','=',value),('model','=','sale.order.line')])
                                            if attr_id:
                                                attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_id[0])], limit=1)
                                            if attr_option_obj:
                                                attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])
                                            if attr_option_data['price'] == 'per_unit':
                                                price_per_unit += attr_option_data['cost_price']
                                price_per_unit += price_per_unit
                                po_dict.update({
                                'partner_id':dict_group_vendor[key]['vendor_id'],
                                'origin':order.name,
                                'date_order':order.date_order,
                                'location_id':12,
                                'pricelist_id':order.pricelist_id.id,
                                'sale_order_id':order.id,
                                'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/',
                                'company_id':order.company_id.id,
                                 })
                                purchase_order_exist=po_obj.search(cr,uid,[('sale_order_id','=',order.id),('partner_id','=',dict_group_vendor[key]['vendor_id'])])
                                if not purchase_order_exist:
                                    po_create=po_obj.create(cr,uid,po_dict,context)
                                    po_line_dict.update({
                                    'product_id':line.product_id.id,
                                    'order_id':po_create,
                                    'name':line.name,
                                    'product_qty':line.product_uom_qty,
                                    'price_unit':price_per_unit,
                                    'date_planned':order.date_order,
                                    'company_id':line.company_id.id,
                                    'x_version_no':line.x_version and line.x_version.name or False,
                                    'x_drop_no':line.x_version and x_drop_number.name or False,
                                    })
                                    pol_obj.create(cr,uid,po_line_dict,context)
                                else:
                                    po_line_dict.update({
                                    'product_id':line.product_id.id,
                                    'order_id':purchase_order_exist[0],
                                    'name':line.name,
                                    'product_qty':line.product_uom_qty,
                                    'price_unit':price_per_unit,
                                    'date_planned':order.date_order,
                                    'company_id':line.company_id.id,
                                    'x_version_no':line.x_version and line.x_version.name or False,
                                    'x_drop_no':line.x_version and x_drop_number.name or False,
                                    })
                    if dict_vendor:
                        for key,value in dict_vendor.iteritems():
                            if len(dict_vendor[key]['attr_ids'])>0:
                                read_val=sol_obj.read(cr,uid,[line.id],dict_vendor[key]['attr_ids'])[0]
                                read_val.pop('id')
                                for value in read_val:
                                    if read_val.get(value):
                                        if isinstance(read_val[value],tuple):
                                            if len(read_val[value]):
                                                attr_option_data = option_obj.read(cr, uid, read_val[value][0], [])
                                                if attr_option_data['price'] == 'per_unit':
                                                    price_per_unit += attr_option_data['cost_price']
                                        elif isinstance(read_val[value],list):
                                            for attr_option_data in option_obj.read(cr, uid, read_val[value], []):
                                                if attr_option_data['price'] == 'per_unit':
                                                    price_per_unit += attr_option_data['cost_price']
                                        else:
                                            attr_id = attr_obj.search(cr, uid, [('name','=',value),('model','=','sale.order.line')])
                                            if attr_id:
                                                attr_option_obj = option_obj.search(cr, uid, [('attribute_id','=',attr_id[0])], limit=1)
                                            if attr_option_obj:
                                                attr_option_data = option_obj.read(cr, uid, attr_option_obj[0], [])
                                            if attr_option_data['price'] == 'per_unit':
                                                price_per_unit += attr_option_data['cost_price']
                                po_dict.update({
                                'partner_id':dict_vendor[key]['vendor_id'],
                                'origin':order.name,
                                'date_order':order.date_order,
                                'location_id':12,
                                'pricelist_id':order.pricelist_id.id,
                                'sale_order_id':order.id,
                                'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/',
                                'company_id':order.company_id.id,
                                 })
                                purchase_order_exist=po_obj.search(cr,uid,[('sale_order_id','=',order.id),('partner_id','=',dict_vendor[key]['vendor_id'])])
                                if not purchase_order_exist:
                                    po_create=po_obj.create(cr,uid,po_dict,context)
                                    po_line_dict.update({
                                    'product_id':line.product_id.id,
                                    'order_id':po_create,
                                    'name':line.name,
                                    'product_qty':line.product_uom_qty,
                                    'price_unit':price_per_unit,
                                    'date_planned':order.date_order,
                                    'company_id':line.company_id.id,
                                    'x_version_no':line.x_version and line.x_version.name or False,
                                    'x_drop_no':line.x_drop_number and line.x_drop_number.name or False,
                                    })
                                    for pol in dict_vendor[key]['attr_ids']:
                                        pol_obj.create(cr,uid,po_line_dict,context)
                                else:
                                    po_line_dict.update({
                                    'product_id':line.product_id.id,
                                    'order_id':purchase_order_exist[0],
                                    'name':line.name,
                                    'product_qty':line.product_uom_qty,
                                    'price_unit':price_per_unit,
                                    'date_planned':order.date_order,
                                    'company_id':line.company_id.id,
                                    'x_version_no':line.x_version and line.x_version.name or False,
                                    'x_drop_no':line.x_version and x_drop_number.name or False,
                                    })
                                    pol_obj.create(cr,uid,po_line_dict,context)
        return True



#           
    def show_invoice(self,cr,uid,ids,context=None):
         mod_obj = self.pool.get('ir.model.data')
         res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
         res_id = res and res[1] or False
         invoice_id=self.pool.get('account.invoice').search(cr,uid,[('origin','=',self.browse(cr,uid,ids[0]).name)])
         return{
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'view_id': [res_id],
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': "{'type':'out_invoice'}",
                'res_id':invoice_id[0]
                }

    def state_review(self,cr,uid,ids,context=None):
        for each in self.browse(cr,uid,ids):
            if not each.order_line:
              raise osv.except_osv(_('Error!'), _('Order Lines are not mentioned'))
            else:
                self.write(cr,uid,[each.id],{'state':'review'})
        return True

    def act_draft(self,cr,uid,ids,context=None):
        for each in self.browse(cr,uid,ids):
            self.write(cr,uid,[each.id],{'state':'draft'})
        return True

    def act_approve(self,cr,uid,ids,context=None):
        for each in self.browse(cr,uid,ids):
            new_line_vals={}
            self.write(cr,uid,[each.id],{'state':'approved'})
            if each.x_signed_flag and each.old_price_total != each.amount_total:
                new_group_ids=self.pool.get('res.groups').search(cr,uid,[('notify_email','in',['notify_account','notify_manager','notify_both'])])
                invoice_id=self.pool.get('account.invoice').search(cr,uid,[('origin','=',each.name)])
                if invoice_id and self.pool.get('account.invoice').browse(cr,uid,invoice_id[0]).state=='draft':
                    for line in each.order_line:
                        product_categ_account=0
                        for account_lines in line.product_id.categ_id.account_lines_ids:
                            sales_team=account_lines.sales_team_id.member_ids
                            sales_person_name=[user.name for user in sales_team]
                            if each.user_id.name in sales_person_name:
                                product_categ_account = account_lines.income_account_id and account_lines.income_account_id.id
                            else:
                                raise osv.except_osv(_('Error!'), _('\n Sales Team: "%s" \n does not have member: "%s" for the Product: "%s" and Product Category: "%s" \n no Incone Account is not define')%(account_lines.sales_team_id.name,each.user_id.name,line.product_id.name,line.product_id.categ_id.name))
                        if product_categ_account==0:
                            raise osv.except_osv(_('Error!'), _('Account not defined for the Selected Product Category'))
                        line_id=[]
                        list_l= [y.id for y in line.tax_id]
                        line_id=self.pool.get('account.invoice.line').search(cr,uid,[('sale_order_line_id','=',line.id),('invoice_id','=',invoice_id[0])])
                        if line_id:
                            self.pool.get('account.invoice.line').write(cr,uid,line_id[0],{'quantity':line.product_uom_qty,'price_unit':line.price_unit,'invoice_line_tax_id':[(6, 0, list_l)]},context)
                        line_id2=self.pool.get('account.invoice.line').search(cr,uid,[('invoice_id','=',invoice_id[0])])
                        new_line_vals.update({'product_id':line.product_id.id,
                        'name':line.name,
                        'quantity':line.product_uom_qty,
                        'price_unit':line.price_unit,
                        'invoice_line_tax_id':[(6, 0, list_l)],
                        'invoice_id':invoice_id[0],
                        'sale_order_line_id':line.id,
                        'account_id':product_categ_account})

                        if line_id2 and not line_id:
                            self.pool.get('account.invoice.line').create(cr,uid,new_line_vals,context)
                for follower_id in self.pool.get('res.groups').browse(cr,uid,new_group_ids):
                    for users in follower_id.users:
                        if users.email and users.partner_id.email:
                            mail_mail = self.pool.get('mail.mail')
                            # the invite wizard should create a private message not related to any object -> no model, no res_id
                            mail_id = mail_mail.create(cr, uid, {
                                'model': 'sale.order',
                                'res_id': each.id,
                                'subject': _('Modification in Quotation # %s') % (each.name,),
                                'body_html': 'This is to notify that Total Amount for %s Quotation is changed' % (each.name,),
                                'auto_delete': True,
                                }, context=context)
                            mail_mail.send(cr, uid, [mail_id], recipient_ids=[users.partner_id.id], context=context)
            if not each.x_signed_flag:
                for line in each.order_line:
                    attr_name=[]
                    if line.attribute_set_id:
                        for attrs_group in line.attribute_set_id.attribute_group_ids:
                            for attrs in attrs_group.attribute_ids:
                                if attrs.attribute_id.required_on_views:
                                    attr_name.append(attrs.name)
                        if len(attr_name)>0:
                            read_line=self.pool.get('sale.order.line').read(cr,uid,[line.id],attr_name)[0]
                            for record in read_line:
                                if not read_line[record]:
                                    raise osv.except_osv(_('Error!'), _('Mandatory Attribute %s cannot be False for the Product \n %s')%(record,line.product_id.name))
        return True

    def act_waiting_for_approve(self,cr,uid,ids,context=None):
        print"waiting for approve"
        for each in self.browse(cr,uid,ids):
            self.write(cr,uid,[each.id],{'state':'waiting_approved_signature'})
            print "method write"
        return True

    def act_reject_signature(self,cr,uid,ids,context=None):
        for each in self.browse(cr,uid,ids):
            self.write(cr,uid,[each.id],{'state':'approved'})
        return True

    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'quoteflow', 'email_send_signing_id_approve')[1]
            
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    _columns={
    'state':fields.selection([('draft','Draft'),('review',' In Review'),('approved','Approved'),('waiting_approved_signature','Waiting Signature Approval'),('quote_cancel','Cancelled')],'State',readonly=True),
    'billing_vendors':fields.selection([('chrysler','Chrysler'),('gm','GM'),('shift_digital','Shift Digital'),('dealer','Dealer')],"Billing Vendors"),
    }

    _defaults={
    'state':'draft'
    }

    def write(self,cr,uid,ids,vals,context=None):
        print" wat is vals",vals
        if vals.get('state')!="waiting_approved_signature" and vals.get('state')!="quote_cancel":
            res = self.read(cr,uid,ids,['state'])
            state_status=res[0].get('state')
            if state_status=="approved":
                 vals.update({'state':'draft'})
                 new_group_ids=self.pool.get('res.groups').search(cr,uid,[('notify_email','=','notify_manager')])
                 
                 for each in self.browse(cr,uid,ids):
                     if each.x_signed_flag:
                         invoice_id=self.pool.get('account.invoice').search(cr,uid,[('origin','=',each.name)])
                         if invoice_id and self.pool.get('account.invoice').browse(cr,uid,invoice_id[0]).state=='open':
                             for follower_id in self.pool.get('res.groups').browse(cr,uid,new_group_ids):
                                for users in follower_id.users:
                                    if users.email and users.partner_id.email:
                                        mail_mail = self.pool.get('mail.mail')
                                        # the invite wizard should create a private message not related to any object -> no model, no res_id
                                        mail_id = mail_mail.create(cr, uid, {
                                            'model': 'sale.order',
                                            'res_id': ids[0],
                                            'subject': _('Modification in Quotation # %s') % (each.name),
                                            'body_html': 'This is to notify that Total Amount for %s Quotation is changed' % (each.name,),
                                            'auto_delete': True,
                                            }, context=context)
                                        mail_mail.send(cr, uid, [mail_id], recipient_ids=[users.partner_id.id], context=context)
        return super(sale_order,self).write(cr,uid,ids,vals,context)

sale_order()



