from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree

class product_product(osv.Model):
    _inherit = "product.product"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and context.get('attribute_group_ids'):
            doc = etree.XML(result['arch'])
            
            for node in doc.xpath("//notebook[@name='attributes_notebook']/page/group"):
                for new in node.xpath('//field'):
                    new.set('required','False')
                    new.set('modifiers','{}')
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

product_product()

class base_product_template(osv.osv):
    _name='base.product.template'

    def _attr_grp_ids(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for i in ids:
            set_id = self.read(cr, uid, [i], fields=['attribute_id'],
                     context=context)[0]['attribute_id']
            if not set_id:
                res[i] = []
            else:
                res[i] = self.pool.get('attribute.group').search(cr, uid,
                      [('attribute_set_id', '=', set_id[0])])
        return res

    _columns = {
        'name':fields.char('Name', size=256, required=True),
        'attribute_group_ids': fields.function(_attr_grp_ids, type='many2many',
        relation='attribute.group', string='Groups'),
        'attribute_id':fields.many2one('attribute.set', 'Attribute Set', required=True),
        'product_id':fields.many2one('product.product', 'Product', required=True),
        'active':fields.boolean('Active'),
    }

    def open_attributes(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'template_attributes_form_view']], context=context)
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

        result = super(base_product_template, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
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
                for new in node.xpath('//field'):
                    new.set('required','False')
                    
                    new.set('modifiers','{}')

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
    _defaults={
            'active': True
            }

base_product_template()


class base_product_bundle(osv.osv):
     _name='base.product.bundle'
     _columns={
        'name':fields.char('Name', size=256, required=True),
        'template_id':fields.many2many('base.product.template', 'bundle_template_rel','temp_id','bundle_id','Product Template'),
        'active':fields.boolean('Active'),
    }
     _defaults={
            'active': True
            }
base_product_bundle()
