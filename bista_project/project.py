# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
from datetime import datetime, date
from openerp.osv import fields, osv
from lxml import etree
from openerp.addons.resource.faces import task as Task
from dateutil import parser
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class project_project(osv.osv):
    _inherit="project.project"

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


    def open_attributes(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'project_attributes_form_view']], context=context)
        if ir_model_data_id:
            res_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']
        grp_ids = self._attr_grp_ids(cr, uid, [ids[0]], [], None, context)[ids[0]]
        ctx = {'open_attributes': True, 'attribute_group_ids': grp_ids}

        return {
            'name': 'Project Attributes',
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

#    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        if context is None:
#            context = {}
#
#        def translate_view(source):
#            """Return a translation of type view of source."""
#            return translate(
#                cr, None, 'view', context.get('lang'), source
#            ) or source
#
#        result = super(project_project, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
#        if view_type == 'form' and context.get('attribute_group_ids'):
#            eview = etree.fromstring(result['arch'])
#            #hide button under the name
#            button = eview.xpath("//button[@name='open_attributes']")
#            if button:
#                button = button[0]
#                button.getparent().remove(button)
#            attributes_notebook, toupdate_fields = self.pool.get('attribute.attribute')._build_attributes_notebook(cr, uid, context['attribute_group_ids'], context=context)
#            result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))
#            if context.get('open_attributes'):
#                placeholder = eview.xpath("//separator[@string='attributes_placeholder']")[0]
#                placeholder.getparent().replace(placeholder, attributes_notebook)
#            elif context.get('open_product_by_attribute_set'):
#                main_page = etree.Element(
#                    'page',
#                    string=translate_view('Custom Attributes')
#                )
#                main_page.append(attributes_notebook)
#                info_page = eview.xpath(
#                    "//page[@string='%s']" % (translate_view('Information'),)
#                )[0]
#                info_page.addnext(main_page)
#            result['arch'] = etree.tostring(eview, pretty_print=True)
#            doc = etree.XML(result['arch'])
#
#            for node in doc.xpath("//notebook[@name='attributes_notebook']/page/group"):
#                for new in node.xpath('//field'):
#
#                    new.set('readonly','True')
#                    new.set('modifiers','{}')
#
#            result['arch'] = etree.tostring(doc)
#        return result

    def field_change(self, cr, uid, ids, field_id, context=None):
        res = {}
        res['value'] = {}
        if field_id:
            filter_ids = self.pool.get('attribute.attribute').search(cr, uid, [('domain_field_id','=',field_id)])
            if filter_ids:
                for val in self.pool.get('attribute.attribute').read(cr, uid, filter_ids, ['name']):
                    res['value'].update({str(val['name']):False})
        return res


   

  

    def create_project(self,cr,uid,ids,context=None):
#        project_obj = self.pool.get('project.project')
        dict={}
        so_obj=self.pool.get('sale.order')

        for each in so_obj.browse(cr,uid, ids):
            
            for line in each.order_line:
                dict.update({
                    'name':each.name+" "+line.product_id.name_template,
                    'partner_id':each.partner_id and each.partner_id.id or False,
                    'attribute_set_id': line.attribute_set_id and line.attribute_set_id.id or False,
                    'sol_id':line.id,
                                 })
                attr_name_in_product=[]
                attr_type_in_product=[]
                
                if line.attribute_set_id:
                    attribute_set_val= line.attribute_set_id.attribute_group_ids         
                    for all in attribute_set_val:
                        for y in all.attribute_ids:                    
                            attr_name_in_product.append(y.attribute_id.name)
                            attr_type_in_product.append(y.attribute_id.attribute_type)
                            read_data= self.pool.get('sale.order.line').read(cr,uid,line.id,attr_name_in_product)

                    for every in read_data:
                        if isinstance(read_data[every],tuple):
                            read_data[every]= read_data.get(every)[0]
                        elif isinstance(read_data[every],list):
                            read_data[every]= [(6,0,read_data.get(every))]
                        else:
                            read_data[every]= read_data.get(every)
                    read_data.pop('id')
                    dict.update(read_data)
                    
                self.create(cr, uid, dict, context=None)
        return True

    
   

    _columns={
        'sol_id':fields.many2one('sale.order.line','Sale order Line',),
        'attribute_set_id':fields.many2one('attribute.set','Attribute Set'),
        'so_id':fields.many2one('sale.order','Quotation'),
        'project_code':fields.char('Project Code',size=6,readonly=True),
        'desc':fields.text('Description',size=10),
	'is_create': fields.boolean('Created')

    }
    
   
#    def onchange_so_id(self, cr, uid, ids, so_id, contex=None):
#        print "helooooooooooooooooooooooooooooooo"
#        so_obj=self.pool.get('sale.order')
#        print "so_obj", so_obj
#        so_brw=so_obj.browse(cr, uid, so_id)
#        print "so_brw", so_brw
#        dict = {}
#        for a in so_brw:
#            print "a====", a
#            dict.update({
#                      'name': a.name,
#                      'partner_id':a.partner_id and a.partner_id.id or False,})
#        self.create(cr, uid, dict, context=None)



#        return dict



    def create(self,cr,uid,vals,context=None):
        vals.update({'project_code':self.pool.get('ir.sequence').get(cr, uid, 'project.project') or '', 'is_create':True})
        res=super(project_project,self).create(cr,uid,vals,context)
        return res


#    def schedule_tasks(self, cr, uid, ids, context=None):
#        res=super(project_project, self).schedule_tasks(cr, uid, ids, context)
#        project = self.browse(cr, uid, ids)
#        task_obj=self.pool.get('project.task')
#        working_time= project[0].resource_calendar_id and project[0].resource_calendar_id.id or False
#
#        total_hrs = 0
#        hrs="23:59:59"
#        project_end = project[0].date+" "+hrs
#
#
#        for a in project:
##            for task in a.tasks:
#             last_task=self.pool.get('project.task').search(cr, uid,[('project_id', '=', a.id)],limit=1,order='id desc')
#
#             for last in task_obj.browse(cr, uid, last_task):
#
##                if task.state in ('done','cancelled'):
##                    continue
#                 print "relativedelta(hours=last.planned_hours", relativedelta(hours=last.planned_hours)
#                 project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                 print "project_end2-relativedelta(hours=last.planned_hours)", project_end2-relativedelta(hours=last.planned_hours)
#                 task_start = project_end2-relativedelta(hours=last.planned_hours)
#                 project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#                 task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#                 print "project_end2project_end2 , project_end2", project_end2, last.name
#                 print "project_end2project_end2 , project_end2", task_start
#                 total_hrs += last.planned_hours
#
#                 task_obj.write(cr, uid, [last.id], {
#                     'date_end': project_end2,
#                     'date_start': task_start,
#
#                     }, context=context)
#
#
##                 if last.predecessor_ids:
#
#
#
#
#
#
#
#
##                    for predecessor in task.predecessor_ids:
##                        difference=strptime(predecessor.planned_hours/9,  "%Y-%m-%d %H:%M:%S")
##                        self.pool.get('project.task').write(cr, uid, [predecessor.id], {
##                        'date_end': a.date,
##                        'date_start': task.date_start - difference
##                         }, context=context)
##
#
#
#        return
#
#
#
##                self.pool.get('project.task').search(cr, uid,[('project_id', '=', ids[0])],limit=1,order="id desc")
#
##                for predecessor in task.predecessor_ids:
##                    print "predecessor.planned_hourspredecessor.planned_hours", predecessor.planned_hours
##                    difference= predecessor.planned_hours/45
##                    print "difference", difference
##                    print "a.dateeeeeeeeeeeee", a.date
##                    print "relativedelta(hours=48)", relativedelta(hours=45)
##
##                    self.pool.get('project.task').write(cr, uid, [predecessor.id+1], {
##                    'date_end': a.date,
##                    'date_start': a.date-project_end,
##                }, context=context)
##

project_project()

class project_task(osv.osv):
    _inherit='project.task'
    def _get_assign_task(self, cr, uid, ids, context=None):
	#users=[]
	print "ids============", ids, uid
	#users=users.append(uid)
	#print "usera 11111111111111", users
	#assigned_user=self.browse(cr, uid, ids)
	#print "assigned_user=======", assigned_user
	
	#users=users.append(user_id)
	
	return [(6,0,[uid])]

    _columns={

	'user_task_ids':fields.many2many('res.users','user_task_rel','user_id','task_id','Assign Task'),
	'visible_task':fields.boolean('Task Visibility'),
	'planned_days':fields.integer('Initially Planned Days'),

    }
    _defaults={
	#'user_task_ids': _get_assign_task,
    	'visible_task':False,
	}

    def create(self, cr, uid, vals, context=None):
        print "==========task_visibility function============", vals, vals['user_id'], uid
        print "vals['predecessor_ids'] vals['predecessor_ids']==", vals.get('predecessor_ids'), vals['successor_ids']
	users_list=[]
	#users_list=users_list.append(uid)
	print "users=========", users_list
	if vals['planned_days']==0 or not vals['planned_days'] :
	    raise osv.except_osv(_('Warning!'), _('Please specify Planned Days'))

#        if vals['predecessor_ids']:
#            print "vals['predecessor_ids']vals['predecessor_ids']", vals['predecessor_ids']
#            vals.update({'visible_task':True})

	if vals['planned_days']:
	    days=vals['planned_days']*24
	    vals.update({'planned_hours':days})

	if vals['user_id'] :
#	    users_list= users_list.append(uid)
#	    print "users_listusers_listusers_list", users_list
#            users_list=users_list.append(vals['user_id'])
#            print "users_listusers_listusers", users_list
	    vals.update({'user_task_ids':[(6,0,[vals['user_id']])]})
#            vals.update({'user_task_ids':[(6,0,users_list)]})
        res=super(project_task,self).create(cr,uid,vals,context)
        task=self.browse(cr, uid, res)
        if not task.predecessor_ids:
            self.write(cr, uid, [res], {'visible_task':True})

        if vals.get('predecessor_ids') and vals.get('successor_ids'):
            print "===========i am in side==========="
            for each in vals['predecessor_ids']:
               if isinstance(each,list):
                    print "each and list", each, list, each[2]
                    for every in each[2]:
                        print "every======", every
                        for successeor in vals['successor_ids']:
                            if isinstance(successeor,list):
                                print "each and list", successeor, list, successeor[2]
                                for all in successeor[2]:
                                    if every==all:
                                        raise osv.except_osv(_('Note !'), _('Same task can not be added as Predecessor and Successor'))
#                               for all in successeor[2]:

           
        return res

    def action_close(self, cr, uid, ids, context=None):
        res=super(project_task, self).action_close(cr, uid, ids, context)
        print "ids=======", ids, res
        task=self.browse(cr, uid, ids, context)[0]
        list=[]
        print "task=========", task, task.successor_ids, self.browse(cr, uid, [task.id], context)[0].successor_ids
        
        for each in task.successor_ids:
	    print "==========in for loop==========",each, each.predecessor_ids
            for every in each.predecessor_ids:
		print "every========", every, every.visible_task
                if every.visible_task==True:
                    list.append(every.id)
		    print "List==========", list
            if len(list)==len(each.predecessor_ids):
                self.write(cr, uid, [each.id],{'visible_task':True}, context)
                print "Value writed for task visisbility========"
            
        
        return res

    def write(self, cr, uid, ids, vals, context=None) :
        if not isinstance(ids,list):
            ids=[ids]
        super(project_task, self).write(cr, uid, ids, vals, context=context)
        current_task=self.browse(cr, uid, ids)
        print "current_task", current_task
        if vals.get('predecessor_ids'):
            vals.update({'visible_task':False})
            print "vals0000000", vals

#        if not vals.get('predecessor_ids'):
#            vals.update({'visible_task':True})
#            print "vals00001111", vals
        if vals.get('successor_ids'):
            for task in current_task:
                for successor in task.successor_ids:
                    self.write(cr, uid, [successor.id], {'visible_task':False})
                    
        if vals.get('user_id'):
            vals.update({'user_task_ids':[(6,0,[vals['user_id']])]})

        if vals.get('planned_days'):
            days=vals['planned_days']*24
            print "days========", days
            vals.update({'planned_hours':days})
        for each_task in current_task:
            print "each_task====", each_task
            if each_task.successor_ids and each_task.predecessor_ids:
                print "current_task.successor_ids==", each_task.successor_ids
                print "current_task.predecessor_ids==", each_task.predecessor_ids
                for every in each_task.predecessor_ids:
                    for each in each_task.successor_ids:
                        if every==each:
                            raise osv.except_osv(_('Note !'), _('Same task can not be added as Predecessor and Successor'))

        
        if vals.get('stage_id'):
            
            for every_task in current_task:
                if every_task.predecessor_ids:
                    for predecessors in every_task. predecessor_ids:
                        if predecessors.state == 'open' or predecessors.state == 'draft' or predecessors.state == 'pending' or predecessors.state == False :
                            raise osv.except_osv(_('Note !'), _('You can not edit this task until predecessors are open '))

        for each in current_task:
            if each.predecessor_ids and vals.get('work_ids'):
                raise osv.except_osv(_('Warning !'), _('You can not fill Timesheet untill Predecessor task is not Done '))
	print "final vals of write=========", vals
        return super(project_task, self).write(cr, uid, ids, vals, context=context)


    
