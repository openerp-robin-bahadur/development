from openerp.osv import fields, osv
from openerp.tools.translate import _


class project_template_wizard(osv.osv_memory):
    _name='project.template.wizard'

    _columns = {
                'template_id':fields.many2one('project.project','Template',required=True),
                'project_id':fields.many2one('project.project','Project',required=True),
                }

    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        active_id = context.get('active_id',[]) or []
        res = super(project_template_wizard, self).default_get(cr, uid, fields, context)
        if active_id:
            if 'project_id' in fields:
                res.update({'project_id':active_id})
        return res

    def choose_template(self, cr, uid, ids, context=None):
        pro_obj=self.pool.get('project.project')
        task_obj=self.pool.get('project.task')
        vals={}
        stage=[]
        member=[]
        task=[]
        for each in self.browse(cr, uid, ids, context):
            for each1 in each.template_id.type_ids:
                stage.append(each1.id)
            for each2 in each.template_id.members:
                member.append(each2.id)
            qry = "select id from project_task where project_id='"+str(each.template_id.id)+"'"
            cr.execute(qry)
            temp = cr.fetchall()
            for task1 in temp:
                defaults = {'project_id':each.project_id.id,
                            'active':True,
                            'date_start': False,
                            'date_end':False,
                            'date_deadline':False
                            }
                task_obj.copy(cr, uid, task1[0], defaults)
                print "temp=", temp
                print "task1[0]=", task1[0]

         
            vals.update({
                    'priority':each.template_id.priority,
                    'parent_id':each.template_id.parent_id.id,
                    'type_ids':[(6,0,stage)],
                    'members':[(6,0,member)]
                })

            print "vals========", vals

        pro_obj.write(cr,uid,context.get('active_ids'),vals,context)

        return vals
project_template_wizard()
