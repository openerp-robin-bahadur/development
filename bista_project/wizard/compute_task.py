from datetime import datetime, date
from openerp.osv import fields, osv
from lxml import etree
from openerp.addons.resource.faces import task as Task
from dateutil import parser
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class project_compute_tasks(osv.osv_memory):
    _inherit = 'project.compute.tasks'

    def task_predecessor(self, cr, uid, task_start, task_ids, context):
        task_obj= self.pool.get('project.task')
        for each in task_ids:
#            print "check after 4 th task...for 1st task....outside if...", pre_end
            if each.date_end and each.date_end < task_start:     #not executed this if while (task_start of 4th task=20 & date_end for task 1=17)
                pre_end=datetime.strptime(each.date_end, "%Y-%m-%d %H:%M:%S")
            elif each.date_end and each.date_end > task_start:
                pre_end=datetime.strptime(task_start, "%Y-%m-%d %H:%M:%S")
            elif task_start:
                pre_end=datetime.strptime(task_start, "%Y-%m-%d %H:%M:%S")
            print "===task_predecessor===task_start=======",task_start
                
            pre_start=pre_end-relativedelta(hours=each.planned_hours)
            pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
            pre_end=pre_end.strftime("%Y-%m-%d %H:%M:%S")
            print "predecessor_ids , start date", pre_end, each.name
            print "predecessor_ids , task start", pre_start, each.planned_hours
            task_obj.write(cr,uid,[each.id],{
               'date_end':pre_end,
               'date_start': pre_start,
                }, context)
            if each.predecessor_ids:
                for line in each.predecessor_ids:
                    print "=======pre_start========",pre_start
                    self.task_predecessor(cr,uid, pre_start, [line], context)


        return

    def task_successor(self, cr, uid, pre_task, task_ids, context):
        task_obj= self.pool.get('project.task')
        for new_id in task_ids:
            task_start = False
            if new_id.successor_ids:
                for line in new_id.successor_ids:
                    self.task_successor(cr,uid, new_id, [line], context)

            if not new_id.successor_ids:
#Bhakthi remember if there is no successor, then obviously predecessor would be there. Otherwise this task weren't here. So use its predecessor's #project's end date 
                project=new_id.project_id
                hrs="15:59:59"
		print "friday afternoon===========", new_id, project, new_id.project_id, new_id.project_id.date
                project_end = new_id.project_id.date+" "+hrs
                project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
                print "original project_end2", project_end2
                task_start = project_end2-relativedelta(hours=new_id.planned_hours)
                project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
                task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
                print "successor_ids , start date", project_end2, new_id.name
                print "successor_ids , task start", task_start, new_id.planned_hours
                task_obj.write(cr, uid, [new_id.id], {
                           'date_end':project_end2,
                           'date_start': task_start,
                            }, context)
                            
            if new_id.predecessor_ids:
                for line in new_id.predecessor_ids:
                    if task_start:
                        self.task_predecessor(cr,uid, task_start, [line], context)


        return

    def new_schedule_task(self, cr, uid, ids, context=None):
#        res=super(project_project, self).schedule_tasks(cr, uid, ids, context)
        read=self.read(cr,uid,ids,[])[0]
        project_id = read['project_id'][0]
        project=self.pool.get('project.project').browse(cr,uid, project_id)
        print "project", project
        task_obj=self.pool.get('project.task')
        working_time= project.resource_calendar_id and project.resource_calendar_id.id or False
        print "project[0].date", project.date
        total_hrs = 0
        hrs="15:59:59"
	if project.date:
            project_end = project.date+" "+hrs
            all_task=self.pool.get('project.task').search(cr,uid,[('project_id', '=',project.id)])
            print "all_task", all_task
	
	
       	    for task_brw in self.pool.get('project.task').browse(cr,uid,all_task):
                print "=======task=========",task_brw.name, task_brw
                if task_brw.successor_ids:
                    for line in task_brw.successor_ids:
                        self.task_successor(cr, uid, task_brw, [line], context)
#            if task_brw.predecessor_ids:
#                print "=====predecessor_ids========"
#                for line in task_brw.predecessor_ids:
#                    self.task_predecessor(cr, uid, task_brw, [line], context)
                if not (task_brw.successor_ids or task_brw.predecessor_ids):
                    project=task_brw.project_id
                    hrs="15:59:59"
                    project_end = task_brw.project_id.date+" "+hrs
                    project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
                    print "original project_end2", project_end2
                    pre_end=project_end2
                    project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")

                    task_data = task_obj.browse(cr, uid, task_brw.id)

                    if not task_data.date_end:
                        pre_end=datetime.strptime(project_end2, "%Y-%m-%d %H:%M:%S")
                    
                    else:
                        pre_end=datetime.strptime(task_data.date_end, "%Y-%m-%d %H:%M:%S")

#                    if not task_data.date_start:
                    pre_start=pre_end-relativedelta(hours=task_data.planned_hours)
#                    else:
#                        pre_start=datetime.strptime(task_data.date_start, "%Y-%m-%d %H:%M:%S")


                    pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
                    pre_end=pre_end.strftime("%Y-%m-%d %H:%M:%S")

                    print "main function , start date", pre_end, task_brw.name
                    print "main function , task start", pre_start, task_brw.planned_hours
                    task_obj.write(cr,uid,[task_brw.id],{
                          'date_end':pre_end,
                          'date_start': pre_start,
                           }, context)


        else:
	    raise osv.except_osv(_('Warning!'),
                _('Please Specify The End Date Of %s')%(project.name))
	

	self.compute_project_start(cr, uid, project, context)
        return


    def compute_project_start(self, cr, uid, project_brw, context):
#	date="3000-12-31 0:0:0"
#	date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#	print "date at starting=======", date
#        print "Tasks of this project", project_brw.tasks
        a=project_brw.date
        print "a=============", a
        for every in project_brw.tasks:
            task = self.pool.get('project.task').browse(cr, uid, [every.id][0])
            if task.date_start and task.date_start<a:
                print "in first if without browse"
                a=self.pool.get('project.task').browse(cr, uid, [every.id][0]).date_start
                print "a=============", a
        if not project_brw.date_start :
            project_start=a
            print "a=============", project_start
        else :
            hrs="0:0:0"
            project_start=project_brw.date_start+" "+hrs

        project_start=datetime.strptime(project_start, "%Y-%m-%d %H:%M:%S")
        project_start=project_start.strftime("%Y-%m-%d")
        self.pool.get('project.project').write(cr, uid, [project_brw.id], {'date_start':project_start}, context)
#	for every in project_brw.tasks:
#
#	    if every.date_start:
#                if every.project_id and not every.project_id.date_start:
#                    project_start=every.date_start
#                else:
#                    hrs="23:59:59"
#                    project_start_date=every.project_id.date_start+" "+hrs
#                    project_start=datetime.strptime(project_start_date, "%Y-%m-%d %H:%M:%S")
#
#                project_start=datetime.strptime(project_start, "%Y-%m-%d %H:%M:%S")
#
#		if project_start<date :
#		    date=project_start
#        print "======final date=======", date
#	self.pool.get('project.project').write(cr, uid, [project_brw.id], {'date_start':date}, context)
#
	return

   





















#        task_id=self.pool.get('project.task').browse(cr, uid, id)
#        print "task_is======", task_id, task_id[0], id, task_id[0].successor_ids
#        successor=task_id[0].successor_ids
#        print "successor's browse record===", self.pool.get('project.task').browse(cr,uid,successor[0].id).date_start
#
#        print " successor's fields===", successor[0].date_start
#        successor_start= successor[0].date_start
#        task_end=datetime.strptime(successor_start, "%Y-%m-%d %H:%M:%S")
#        task_start=task_end-relativedelta(hours=task_id[0].planned_hours)
#        task_end= task_end.strftime("%Y-%m-%d %H:%M:%S")
#        task_start=task_start.strftime("%Y-%m-%d %H:%M:%S")
#        print "task_start======", task_start
#        print "task_end=======", task_end
#        self.pool.get('project.task').write(cr,uid,id,{
#                             'date_end':task_end,
#                             'date_start': task_start,
##                             'name': task_id[0].name + "child",
#
#                             }, context=context)
#


#

#                last_task=self.pool.get('project.task').search(cr, uid,[('project_id', '=', project.id)],limit=1,order='id desc')
#
#                    lonely_tasks=[]
#                    lonely_tasks.append()
##                    for each in
#
#                    print "last_taskkkkkk", last_task
#                    for last in task_obj.browse(cr, uid, last_task):



#                if task.state in ('done','cancelled'):
#                    continue
                        
                 
                        
        #                 print "project_end2-relativedelta(hours=last.planned_hours)", project_end2-relativedelta(hours=last.planned_hours)-relativedelta(hours=6)
#                                                print "last=========", last
#                         total_hrs += last.planned_hours
#
#                        
#
#                         for predecessor in task_obj.browse(cr, uid, [last.id]):
#                             print "predecessor", predecessor, predecessor.date_start
#                             for each in predecessor.predecessor_ids:
#
#                                 print "each", each
#
#                                 print "hi i am being called==================="
#
#                                 print "test==========", predecessor, predecessor.date_start, predecessor.planned_hours
#                                 predecessor_end=datetime.strptime(predecessor.date_start, "%Y-%m-%d %H:%M:%S")
#                                 predecessor_start=predecessor_end-relativedelta(hours=each.planned_hours)
#
#                                 predecessor_end=predecessor_end.strftime("%Y-%m-%d %H:%M:%S")
#                                 predecessor_start=predecessor_start.strftime("%Y-%m-%d %H:%M:%S")
#
#                                 print "predecessor start and end", predecessor_start, predecessor_end
#
#
#
#                                 task_obj.write(cr, uid,[each.id], {
#                                 'date_end': predecessor_end,
#                                 'date_start': predecessor_start,
#
#                                 }, context=context)
#        #                         if each.predecessor_ids:
#
#
#
#
#



    #                    for predecessor in task.predecessor_ids:
    #                        difference=strptime(predecessor.planned_hours/9,  "%Y-%m-%d %H:%M:%S")
    #                        self.pool.get('project.task').write(cr, uid, [predecessor.id], {
    #                        'date_end': a.date,
    #                        'date_start': task.date_start - difference
    #                         }, context=context)
    #


       



    #                self.pool.get('project.task').search(cr, uid,[('project_id', '=', ids[0])],limit=1,order="id desc")

    #                for predecessor in task.predecessor_ids:
    #                    print "predecessor.planned_hourspredecessor.planned_hours", predecessor.planned_hours
    #                    difference= predecessor.planned_hours/45
    #                    print "difference", difference
    #                    print "a.dateeeeeeeeeeeee", a.date
    #                    print "relativedelta(hours=48)", relativedelta(hours=45)
    #
    #                    self.pool.get('project.task').write(cr, uid, [predecessor.id+1], {
    #                    'date_end': a.date,
    #                    'date_start': a.date-project_end,
    #                }, context=context)
    #
project_compute_tasks()


