from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class account_invoice(osv.osv):
    _inherit='account.invoice'
    
    def repull_quotation(self,cr,uid,ids,context=None):
        sale_obj = self.pool.get('sale.order')
        invoice_line_obj = self.pool.get('account.invoice.line')
        # infuture we can use this function to repull quotation for multiple invoice at a time
        for invoice in self.browse(cr,uid,ids):
            sale_id = sale_obj.search(cr,uid,[('name','=',invoice.origin)])

            if not sale_id:
                return False
            # there would be only one so\QO associated with the record.
            sale_browse = sale_obj.browse(cr,uid,sale_id[0])
            sale_order_line = sale_browse.order_line
            product_categ_account=0

            sale_team_id=self.pool.get('crm.case.section').search(cr,uid,[('member_ids','in',sale_browse.user_id.id)])
            if not sale_team_id:
                raise osv.except_osv(_('Error!'), _('\n Sales Person %s given in the quotation %s is not associated with any Sales Team')%(sale_browse.name,sale_browse.user_id.name))

            vals = {
                'partner_id':sale_browse.partner_id.id,
                'date_due':sale_browse.x_payment_due_date,
                'account_id':sale_browse.partner_id.property_account_receivable.id,
                'origin':sale_browse.name
            }
            self.write(cr,uid,[invoice.id],vals)
#             unlink the already created invoice line, or else we have another option as itratiing it as well and changing only whats new has edited
            invoice_line_ids =  [line.id for line in invoice.invoice_line]
            invoice_line_obj.unlink(cr,uid,invoice_line_ids)
            for so_line in sale_order_line:
                for account_lines in so_line.product_id.categ_id.account_lines_ids:
                    sales_team=account_lines.sales_team_id.member_ids
                    sales_person_name=[user.name for user in sales_team]
                    if sale_browse.user_id.name in sales_person_name:
                        product_categ_account = account_lines.income_account_id and account_lines.income_account_id.id
                    else:
                        raise osv.except_osv(_('Error!'), _('\n Sales Team: "%s" \n does not have member: "%s" for the Product: "%s" and Product Category: "%s" \n no Incone Account is not define')%(account_lines.sales_team_id.name,sale_browse.user_id.name,so_line.product_id.name,so_line.product_id.categ_id.name))
                if product_categ_account==0:
                    raise osv.except_osv(_('Error!'), _('Account not defined for the Selected Product Category'))

                list_l= [y.id for y in so_line.tax_id]
                product_get=so_line.product_id
                line_vals={
                    'product_id':product_get.id,
                    'name':so_line.name,
#                        'date_planed':x.'date_planed',
                    'quantity':so_line.product_uom_qty,
                    'price_unit':so_line.price_unit,
                    'date_planned':sale_browse.date_order,
                    'invoice_line_tax_id':[(6, 0, list_l)],
                    'invoice_id':invoice.id,
                    'price_unit':so_line.price_unit,
                    'sale_order_line_id':so_line.id,
                    'account_id':product_categ_account
                }
                invoice_line_obj.create(cr,uid,line_vals,context=None)


            mod_obj = self.pool.get('ir.model.data')
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            res_id = res and res[1] or False
            return{
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': [res_id],
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'context': "{'type':'out_invoice'}",
                    'res_id':invoice.id,
                    }
        return True

account_invoice()
