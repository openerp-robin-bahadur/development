# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_attribute.attributes for OpenERP                                     #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>
#   Copyright (C) 2013 Akretion Raphaël VALYI <raphael.valyi@akretion.com>
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import ast
from openerp.osv import orm, fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from lxml import etree
from unidecode import unidecode # Debian package python-unidecode
import re
from osv import osv, fields


class attribute_attribute(orm.Model):
    _inherit = "attribute.attribute"

    def _build_attribute_field(self, cr, uid, main_group, attribute, context=None):
        if attribute.ttype in ['text']:
            parent = etree.SubElement(main_group, 'group', colspan="4", col="4")
        else:
            parent = etree.SubElement(main_group, 'group', colspan="2", col="2")
        kwargs = {'name': "%s" % attribute.name}
        if attribute.ttype in ['text']:
            parent = etree.SubElement(parent, 'group', colspan="4", col="4")
            etree.SubElement(parent,
                                   'separator',
                                    string="%s" % attribute.field_description,
                                    colspan="4")
            kwargs['nolabel'] = "1"
        if attribute.ttype in ['many2many']:
            kwargs['widget'] = "many2many_tags"
        if attribute.ttype in ['many2one', 'many2many']:
            if attribute.used_in_domain:
                kwargs['on_change'] = "field_change(%s)" % attribute.id
            if attribute.relation_model_id:
                # attribute.domain is a string, it may be an empty list
                try:
                    domain = ast.literal_eval(attribute.domain)
                except ValueError:
                    domain = None
                if domain:
                    kwargs['domain'] = attribute.domain
                else:
                    ids = [op.value_ref.id for op in attribute.option_ids]
                    kwargs['domain'] = "[('id', 'in', %s)]" % ids
            else:
                if attribute.domain_field_id:

                    filter_ids=[x.id for x in attribute.domain_field_id.option_ids]
                    kwargs['domain'] = "[('attribute_id', '=', %s),('filter_field_id','in',%s)]" % (attribute.id,attribute.domain_field_id.name)
                else:
                    kwargs['domain'] = "[('attribute_id', '=', %s)]" % attribute.id
        kwargs['context'] = "{'default_attribute_id': %s}" % attribute.id
        kwargs['required'] = str(attribute.required or
                                 attribute.required_on_views)

        field = etree.SubElement(parent, 'field', **kwargs)
        orm.setup_modifiers(field, self.fields_get(cr, uid, attribute.name,
                                                   context))
        return parent

    def _build_attributes_notebook(self, cr, uid, attribute_group_ids,
                                   context=None):
        notebook = etree.Element('notebook', name="attributes_notebook",
                                 colspan="4")
        toupdate_fields = []
        grp_obj = self.pool.get('attribute.group')
        for group in grp_obj.browse(cr, uid, attribute_group_ids,
                                    context=context):
            page = etree.SubElement(notebook, 'page',
                                    string=group.name.capitalize())
            main_group = etree.SubElement(page, 'group', colspan="4", col="4")
            for attribute in group.attribute_ids:
                if attribute.attribute_id.name not in toupdate_fields:
                    toupdate_fields.append(attribute.attribute_id.name)
                    self._build_attribute_field(cr, uid, main_group, attribute.attribute_id,
                                                context=context)
        
        return notebook, toupdate_fields


    def _field_value(self, cr, uid, context=None):
        return [('none', 'None')]
    _columns={
                'active':fields.boolean('Active'),
                'is_create':fields.boolean("create",readonly=True,invisble=True),
                'domain_field_id':fields.many2one('attribute.attribute','Domain Field'),
                'used_in_domain':fields.boolean('Used In Domain',readonly=True),
                    }

    _defaults = {
                 'active':True
                }

    def create(self, cr, uid, vals, context=None):
        """ Create an attribute.attribute
        """

        fields_obj = self.pool.get("ir.model.fields")
        if 'name' in vals and vals['name']:
            old_field = self.search(cr, uid, [('name','=',vals['name'])])
            if not old_field:
                 old_ir_field = fields_obj.search(cr, uid, [('name','=',vals['name'])])
                 if old_ir_field:
                     fields_obj.unlink(cr, uid, old_ir_field)
        global search_model_ids1
        try:
            if search_model_ids1:
                pass
        except:
            search_model_ids1 = []

        vals['state'] = 'manual'

        update_model_ids=self.pool.get('ir.model').search(cr,uid,[('model', 'in',['base.product.template','sale.order.line'])])
        if vals['model_id'] not in update_model_ids and len(vals['option_ids']) == 0:
            raise osv.except_osv(_('Error!'), _('Attribute must have atleast one active option line.'))

        vals['is_create']=True
        res = super(attribute_attribute, self).create(cr, uid, vals, context)
        model = self.browse(cr, uid, res)
        if res:
            if model.model == 'product.product' and not search_model_ids1:
                search_model_ids1=self.pool.get('ir.model').search(cr,uid,[('model', 'in',['base.product.template','sale.order.line'])])
            if model.domain_field_id:
                self.write(cr, uid, [model.domain_field_id.id], {'used_in_domain':True})

        for each in search_model_ids1:
            search_model_ids1.remove(each)
            vals.update({'model_id' : each})
            res_copy_id = self.copy(cr, uid, res, vals, context)

        return res

    def write(self, cr, uid,ids ,vals,context=None):
        """ Write method of attribute.attribute
        """
        global search_model_ids2
        try:
            if search_model_ids2:
                pass
        except:
            search_model_ids2 = []
        sol=self.browse(cr,uid,ids)
        if 'domain_field_id' in vals and vals['domain_field_id']:
            self.write(cr, uid, [vals['domain_field_id']], {'used_in_domain':True})
        if 'domain_field_id' in vals and not vals['domain_field_id']:

            if sol[0].domain_field_id:
                if sol[0].model == 'product.product':
                    for line in sol[0].option_ids:
                        if line.filter_field_id:
                            self.pool.get('attribute.option').write(cr, uid, [line.id], {'filter_field_id':False})
                filter_ids = self.search(cr, uid, [('domain_field_id','=',sol[0].domain_field_id.id),('model','=','product.product')])
                if not filter_ids:
                    self.write(cr, uid, [sol[0].domain_field_id.id], {'used_in_domain':False})
        res = super(attribute_attribute, self).write(cr, uid, ids, vals, context)
        if sol:
            if sol[0].model == 'product.product' and not search_model_ids2:
                search_model_ids2=self.search(cr,uid,[('name','=',sol[0].name),('model', 'in',['base.product.template','sale.order.line'])])


        for each in search_model_ids2:
            if 'option_ids' in vals:
                vals.pop('option_ids')
            search_model_ids2.remove(each)
            self.write(cr, uid, [each], vals, context)

        sol=self.browse(cr,uid,ids)
        if sol:
            if not sol[0].option_ids and sol[0].model == 'product.product':
                raise osv.except_osv(_('Error!'), _('Attribute must have atleast one active option line.'))

        return res

    def unlink(self, cr, uid,ids,context=None):

        fields_obj=self.pool.get("ir.model.fields")
        attr_records = self.browse(cr, uid, ids)
        for each_attr_record in attr_records:
            each_attr_record_name = each_attr_record.name
            if each_attr_record_name in ['x_version','x_sale_start_date','x_sale_end_date','x_drop_number','x_list_type']:
                continue
            attr_field_ids = self.search(cr, uid, [('name','=',each_attr_record_name)])

            ir_field_records = self.browse(cr,uid,attr_field_ids)
            ir_field_records_ids = []
            for each in ir_field_records:
                ir_field_records_ids.append(each.field_id.id)
            fields_obj.unlink(cr, uid, ir_field_records_ids)

        return super(attribute_attribute, self).unlink(cr, uid, ids, context=context)

    def field_change(self, cr, uid, ids, field_id, context=None):
        res = {}
        if not field_id:
            filter_ids = self.search(cr, uid, [('domain_field_id','=',field_id)])
            if filter_ids:
                for val in self.read(cr, uid, filter_ids, ['name']):
                    res['value'].update({str(val.name):False})

        return res

    def check_recursive(self, cr, uid, ids, field_id, context=None):
        res = {}
        if not field_id:
            res['value'] = {}
        if ids:
            if isinstance(ids,list):
                ids = ids[0]
            if ids == field_id:
                warning = {
                            'title': _('Configuration Error!'),
                            'message' : _('Recursive domain is not allowed, Please check the configuration.')
                          }
                res['value'] = {'domain_field_id':False}
                res['warning'] = warning

        return res

attribute_attribute()

class attribute_option(orm.Model):
    _inherit = "attribute.option"
    _columns={
                'name': fields.char('Name', size=64, required=False),
                'active':fields.boolean('Active'),
                'sales_price': fields.float('Sale Price',digits=(4,4)),
                'cost_price': fields.float('Cost Price',digits=(4,4)),
                'price':fields.selection([('per_unit','Per Unit'),('based_order_lines','Per Order Lines')],'Calculation Method'),
                'attribute_id': fields.many2one('attribute.attribute','Product Attribute',required=True,ondelete='cascade'),
                'field_desc':fields.related('attribute_id','field_description',type='char',string="Field Label", store=True),
                'filter_field_id':fields.many2many('attribute.option','attribute_filter_rel','attr_id','filter_id','Filter Value'),
             }

    _defaults = {
                 'active':True,
                 'price':'per_unit',
                }

    def create(self, cr, uid, vals, context=None):

        res = super(attribute_option, self).create(cr, uid, vals, context)
        result = self.read(cr, uid, res, [])
        global search_model_ids3
        try:
            if search_model_ids3:
                pass
        except:
            search_model_ids3 = []
        val = self.browse(cr, uid, res)

        if res:
            if val.attribute_id.model == 'product.product' and not search_model_ids3:
                search_model_ids3 = self.pool.get('attribute.attribute').search(cr, uid, [('name','=',val.attribute_id.name),('model' ,'in',['base.product.template','sale.order.line'])])

        for each in search_model_ids3:
            search_model_ids3.remove(each)
            vals.update({'attribute_id' : each})
            res_copy_id = self.copy(cr, uid, res, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        val = self.browse(cr, uid, ids)
        res = super(attribute_option, self).write(cr, uid, ids, vals, context)

        global search_model_ids4
        try:
            if search_model_ids4:
                pass
        except:
            search_model_ids4 = []

        if res:
            if val[0].attribute_id.model == 'product.product' and not search_model_ids4:
                search_model_ids4 = self.pool.get('attribute.attribute').search(cr, uid, [('name','=',val[0].attribute_id.name),('model' ,'in',['base.product.template','sale.order.line']),('active','=','True')])
        for each in search_model_ids4:
            search_model_ids4.remove(each)
            search_id = self.search(cr, uid, [('attribute_id','=',each)])
            write_id = self.search(cr, uid, [('attribute_id','=',each),('sales_price','=',val[0].sales_price),('sequence','=',val[0].sequence),('cost_price','=',val[0].cost_price),('name','=',val[0].name),('active','=',val[0].active)])
            if write_id:
                self.write(cr, uid, [write_id[0]],vals)
        return res

    def unlink(self, cr, uid,ids,context=None):
        unlink_ids = []
        for val in self.browse(cr, uid, ids):
            search_model_ids5 = self.pool.get('attribute.attribute').search(cr, uid, [('name','=',val.attribute_id.name),('model' ,'in',['base.product.template','sale.order.line']),('active','=','True')])
            for each in search_model_ids5:
                write_ids = self.search(cr, uid, [('attribute_id','=',each),('sales_price','=',val.sales_price),('sequence','=',val.sequence),('cost_price','=',val.cost_price),('name','=',val.name)])
                for each in write_ids:
                    unlink_ids.append(each)
            unlink_ids.append(val.id)
        return super(attribute_option, self).unlink(cr, uid, unlink_ids, context=context)

    def name_change(self, cr, uid, ids, name, field_id, context=None):
        res = {}
        if not field_id:
            res['domain'] = {'filter_field_id':[('id','in',[])]}
            return res
        filter_ids = self.search(cr, uid, [('attribute_id','=',field_id)])
        res['domain'] = {'filter_field_id':[('id','in',filter_ids)]}
        return res

attribute_option()


class attribute_set(osv.osv):
    _inherit='attribute.set'

    _columns={
    'vendor_id':fields.many2one('res.partner','Vendor',domain=[('supplier','=',True)])
    }
    def create(self,cr,uid,vals,context=None):
        if vals['name'] and vals['vendor_id']:
            v_name=self.pool.get('res.partner').browse(cr,uid,vals['vendor_id']).name
            vals.update({'name':vals['name']+" - "+v_name})
        return super(attribute_set,self).create(cr,uid,vals,context)
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        data = self.browse(cr, uid, id)
        default.update({
                        'name': data.name + ' Copy',
                        })
        return super(attribute_set, self).copy(cr, uid, id, default, context=context)

attribute_set()

class attribute_location(orm.Model):
    _inherit = "attribute.location"

    _columns = {
                'name': fields.related(
                'attribute_id',
                'name',
                type='char',
                string='Name',
                readonly=True,
                store=True),
                'vendor_id':fields.many2one('res.partner','Vendor',domain=[('supplier','=',True)]),
                'vendor_group':fields.selection([('group_one','Group 1'),('group_two','Group 2'),('group_three','Group 3'),('group_four','Group 4'),('group_five','Group 5'),('group_six','Group 6'),('group_seven','Group 7'),('group_eight','Group 8'),('group_nine','Group 9'),('group_ten','Group 10'),('group_eleven','Group 11'),('group_twelve','Group 12'),('group_thirteen','Group 13'),('group_fouteen','Group 14'),('group_fifteen','Group 15'),('group_sixteen','Group 16'),('group_seventeen','Group 17'),('group_eighteen','Group 18'),('group_nineteen','Group 19'),('group_twenty','Group 20'),],'Vendor Group')
                }

    _sql_constraints = [
                        ('group_field_uniq', 'unique (attribute_id, attribute_group_id)',
                                'The name of the field is already exist for a given group !'),
                        ]

attribute_location()


class attribute_group(osv.osv):
    _inherit='attribute.group'
    _columns={
    'vendor_id_group':fields.many2one('res.partner','Group Vendor',domain=[('supplier','=',True)]),
    }

    def create(self,cr,uid,vals,context=None):
        dict_vendor_group={}
        res= super(attribute_group,self).create(cr,uid,vals,context)
        if vals['attribute_ids']:
            for each in vals['attribute_ids']:
                if isinstance(each,list):
                    for value in each:
                        if isinstance(value,dict):
                            if value['vendor_group']:
                                if dict_vendor_group and dict_vendor_group.has_key(value['vendor_group']):
                                    if dict_vendor_group.get(value['vendor_group'])!=value['vendor_id']:
                                        raise osv.except_osv(_('Error!'), _('Please select same vendor for the group: %s.')%(value['vendor_group']))
                                else:
                                    dict_vendor_group[value['vendor_group']]=value['vendor_id']
        return res

    def write(self,cr,uid,ids,vals,context=None):
        attr_name=[]
        attr_domain_field=[]
        dict_vendor_group={}
        res= super(attribute_group,self).write(cr,uid,ids,vals,context)
        for each in self.browse(cr,uid,ids):
            for attribute_ids in each.attribute_ids:
                attr_name.append(attribute_ids.name)
                if attribute_ids.attribute_id.domain_field_id:
                    attr_domain_field.append(attribute_ids.attribute_id.domain_field_id.name)
            for name in attr_domain_field:
                if name not in attr_name:
                    raise osv.except_osv(_('Error!'), _('Domain field %s.')%(name +" is not mentioned"))
                else:
                    pass
            for attrs_ids in each.attribute_ids:
                if attrs_ids.vendor_group:
                    if dict_vendor_group and dict_vendor_group.has_key(attrs_ids.vendor_group):
                        if dict_vendor_group.get(attrs_ids.vendor_group)!=attrs_ids.vendor_id.id:
                            raise osv.except_osv(_('Error!'), _('Please select same vendor for the group: %s.')%(attrs_ids.vendor_group))
                    else:
                        dict_vendor_group[attrs_ids.vendor_group]=attrs_ids.vendor_id.id
        return res

attribute_group()