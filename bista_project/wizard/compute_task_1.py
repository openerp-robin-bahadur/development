from datetime import datetime, date
from openerp.osv import fields, osv
from lxml import etree
from openerp.addons.resource.faces import task as Task
from dateutil import parser
from dateutil.relativedelta import relativedelta

class project_compute_tasks(osv.osv_memory):
    _inherit = 'project.compute.tasks'
    
    def task_schedule(self, cr, uid, task_ids, context):
        task_obj= self.pool.get('project.task')
        for new_id in task_obj.browse(cr, uid, task_ids):
            if new_id.successor_ids:
                for line in new_id.successor_ids:
                    self.task_schedule(cr,uid,line, context)

             if not new_id.successor_ids:
                project=new_id.project_id
                hrs="15:59:59"
                project_end = new_id.project_id.date+" "+hrs
                project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
                print "original project_end2", project_end2
                task_start = project_end2-relativedelta(hours=new_id.planned_hours)
                project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
                task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
                print "project_end2project_end2 , project_end2", project_end2, new_id.name
                print "project_end2project_end2 , project_end2", task_start
                task_obj.write(cr, uid, [new_id.id], {
                           'date_end':project_end2,
                           'date_start': task_start,
                            }, context=context)
                
                for each in new_id.predecessor_ids:
                    if each.date_end and each.date_end < new_id.date_start:
                        pre_end=datetime.strptime(new_id.date_start, "%Y-%m-%d %H:%M:%S")
                    elif each.date_end and each.date_end > new_id.date_start:
                        pre_end=datetime.strptime(each.date_end, "%Y-%m-%d %H:%M:%S")
                    else:
                        pre_end=datetime.strptime(new_id.date_start, "%Y-%m-%d %H:%M:%S")

                    pre_start=pre_end-relativedelta(hours=each.planned_hours)
                    pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
                    pre_end=pre_end.strftime("%Y-%m-%d %H:%M:%S")
                    
                    task_obj.write(cr,uid,[each.id],{
                       'date_end':pre_end,
                       'date_start': pre_start,
                        }, context=context)
            
        return

    def new_schedule_task(self, cr, uid, ids, context=None):
#        res=super(project_project, self).schedule_tasks(cr, uid, ids, context)
        read=self.read(cr,uid,ids,[])[0]
        project_id = read['project_id'][0]
        print "project ", project_id
        project=self.pool.get('project.project').browse(cr,uid, project_id)
        print "project", project
        task_obj=self.pool.get('project.task')
        working_time= project.resource_calendar_id and project.resource_calendar_id.id or False
        print "project[0].date", project.date
        total_hrs = 0
        hrs="15:59:59"
        project_end = project.date+" "+hrs
        all_task=self.pool.get('project.task').search(cr,uid,[('project_id', '=',project.id)])
        print "all_task", all_task

#        for task in project.tasks:

#            if not task.predecessor_ids and not task.successor_ids:
#                        print "relativedelta(hours=last.planned_hours", relativedelta(hours=task.planned_hours), project_end, datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                        project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
#                        print "original project_end2", project_end2
#                        task_start = project_end2-relativedelta(hours=task.planned_hours)
#                        project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#                        task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#                        print "project_end2project_end2 , project_end2", project_end2, task.name
#                        print "project_end2project_end2 , project_end2", task_start
#                        task_obj.write(cr, uid, [task.id], {
#                                 'date_end':project_end2,
#                                 'date_start': task_start,
#    #                             'name': task.name + "test",
#
#                                 }, context=context)
#                        print "FIRST WRITE EXECUTED"
#
#            elif task.predecessor_ids and not task.successor_ids:
#
#                print "task..........", task
#                print "relativedelta(hours=last.planned_hours", relativedelta(hours=task.planned_hours), project_end, datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
#                print "original project_end2", project_end2
#                task_start = project_end2-relativedelta(hours=task.planned_hours)
#                project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#                task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#                print "project_end2project_end2 , project_end2", project_end2, task.name
#                print "project_end2project_end2 , project_end2", task_start
#                task_obj.write(cr, uid, [task.id], {
#                    'date_end':project_end2,
#                    'date_start': task_start,
#    #                             'name': task.name + "test",
#
#                     }, context=context)

#            elif task.succesor_ids:
#                print "task..........", task
#                print "relativedelta(hours=last.planned_hours", relativedelta(hours=task.planned_hours), project_end, datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
#                print "original project_end2", project_end2
#                task_start = project_end2-relativedelta(hours=task.planned_hours)
#                project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#                task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#                print "project_end2project_end2 , project_end2", project_end2, task.name
#                print "project_end2project_end2 , project_end2", task_start
#                task_obj.write(cr, uid, [task.id], {
#                    'date_end':project_end2,
#                    'date_start': task_start,
#    #                             'name': task.name + "test",
#
#                     }, context=context)
        for task_brw in self.pool.get('project.task').browse(cr,uid,all_task):
#            each = task_brw.id
#            print "each", each
#            qry = "select task_id from task_predecessors_rel where predecessor_id='"+str(each)+"'"
#            print "qry====", qry
#            cr.execute(qry)
##            task_ids = cr.fetchall()
#            task_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
#            print "temp====", task_ids
#            fsdfd
            if task_brw.successor_ids:
                for line in task_brw.successor_ids:
                    self.task_schedule(cr, uid, [line], context)

#            if task_ids:
#                for each_task_brw in task_obj.browse(cr,uid,task_ids):
##                    each_task_brw = each_task_brw[0]
#                    print "each_task_brw",each_task_brw,each_task_brw.planned_hours
#
#
#    #                        successor=all[1]
#    #                        successor=task_obj.browse(cr, uid, successor, context)
##                    print "suucessor===", successor
#    #                        duration=successor.planned_hours
#    #                        print "duration", duration
#    #                        predecessor=task_obj.browse(cr, uid, each, context)
#                    pre_end=each_task_brw.date_start
#                    print "pre_end", pre_end
#                    pre_end_val=datetime.strptime(pre_end, "%Y-%m-%d %H:%M:%S")
#                    pre_start=pre_end_val-relativedelta(hours=each_task_brw.planned_hours)
#                    pre_end=pre_end_val.strftime("%Y-%m-%d %H:%M:%S")
#                    pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
#                    each_task_brw.write({'date_end':pre_end,
#                             'date_start': pre_start,
#                              }, context=context)
#                    pre_start=pre_end_val + relativedelta(hours=task_brw.planned_hours)
#                    pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
#                    task_obj.write(cr, uid, each, {
#                             'date_end':pre_start,
#                             'date_start': pre_end,
#                              }, context=context)
#
#            else:
#                pre_end = project.date
#                pre_end=datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                print"task_brw.planned_hours",task_brw.planned_hours
#                pre_start=pre_end-relativedelta(hours=task_brw.planned_hours)
#                pre_end=pre_end.strftime("%Y-%m-%d %H:%M:%S")
#                pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
#                task_obj.write(cr, uid, each, {
#                                 'date_end':pre_end,
#                                 'date_start': pre_start,
#                                  }, context=context)
#


#                if duration>duration.planned_hours:
#            hcdhckuhdha
#
#
#
##        nclieqjfivrg
#
#        if project:
#            for task in project.tasks:
#                print "task=================", task
#                if not task.predecessor_ids and not task.successor_ids:
#                    print "relativedelta(hours=last.planned_hours", relativedelta(hours=task.planned_hours), project_end, datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")
#                    project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
#                    print "original project_end2", project_end2
#                    task_start = project_end2-relativedelta(hours=task.planned_hours)
#                    project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#                    task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#                    print "project_end2project_end2 , project_end2", project_end2, task.name
#                    print "project_end2project_end2 , project_end2", task_start
#                    task_obj.write(cr, uid, [task.id], {
#                             'date_end':project_end2,
#                             'date_start': task_start,
##                             'name': task.name + "test",
#
#                             }, context=context)
#                    print "FIRST WRITE EXECUTED"
#
#                elif task.successor_ids:
#                     print "name--------------------",task, task.successor_ids
#
#                     self.task_schedule(cr, uid, task.id, context)
#
#        return
#
#
#    def task_schedule(self, cr, uid, id, context):
#        print "id", id
#        task_obj= self.pool.get('project.task')
#        new_id=task_obj.browse(cr, uid, id, context)
#        print "new_id", new_id
#        if new_id.successor_ids:
#            print "It is there......."
#            print "LOOK AT ME---------", new_id.successor_ids
#            self.task_schedule(cr,uid,new_id.successor_ids[0].id, context)
#
#
#        if not new_id.successor_ids:
#            print "I AM 1199", new_id
#            project=new_id.project_id
#            print "project-------", project
#            hrs="15:59:59"
#            project_end = project.date+" "+hrs
#
##            buefhuieqd
#            project_end2= datetime.strptime(project_end, "%Y-%m-%d %H:%M:%S")-relativedelta(hours=6)
#            print "original project_end2", project_end2
#            task_start = project_end2-relativedelta(hours=new_id.planned_hours)
#            project_end2 = project_end2.strftime("%Y-%m-%d %H:%M:%S")
#
#            task_start = task_start.strftime("%Y-%m-%d %H:%M:%S")
#            print "project_end2project_end2 , project_end2", project_end2, new_id.name
#            print "project_end2project_end2 , project_end2", task_start
#            task_obj.write(cr, uid, [new_id.id], {
#                       'date_end':project_end2,
#                       'date_start': task_start,
#                        }, context=context)
#            print "new_id 0f 1199",new_id, new_id.predecessor_ids
#
#
#            for each in new_id.predecessor_ids:
#                qry = "select id from task_predecessor_rel where task_id='"+str(each.predecessor_id.id)+"'"
#                print "qry====", qry
#                cr.execute(qry)
#                temp = cr.fetchall()
#                print "temp", temp
#
#
#
#
#
#
##            for each in new_id.predecessor_ids:
##
##                 print "each", each, each.predecessor_ids
##                 print "new_id in for======", new_id
##                 new_id=task_obj.browse(cr,uid,[new_id.id],context)
##                 print "new_id", new_id
##                 pre_end=new_id[0].date_start
##                 print "============",pre_end
##                 pre_end=datetime.strptime(pre_end, "%Y-%m-%d %H:%M:%S")
##
##                 pre_start=pre_end-relativedelta(hours=each.planned_hours)
##
##                 pre_end=pre_end.strftime("%Y-%m-%d %H:%M:%S")
##                 pre_start=pre_start.strftime("%Y-%m-%d %H:%M:%S")
##                 task_obj.write(cr,uid,[each.id],{
##                       'date_end':pre_end,
##                       'date_start': pre_start,
##                        }, context=context)
##                 print "semi final new_id", new_id, new_id[0].predecessor_ids[0]
##                 new_id=new_id[0].predecessor_ids[0]
##                 print "new new_id", new_id, each, new_id.predecessor_ids
##[browse_record(project.task, 1198)] browse_record(project.task, 1198) [browse_record(project.task, 1197)]
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


