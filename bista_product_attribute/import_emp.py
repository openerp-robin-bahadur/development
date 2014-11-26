#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 13:03:53 2014

@author: Scott Bowman
"""


import csv, xmlrpclib
from dateutil import parser

do_department = True
update_departments = True

do_jobs = True
update_jobs = True

do_employees = True
update_employees = True


import_file_name = 'attribute.attribute.csv'
host_url = 'http://localhost:8069/xmlrpc/'
user = 'admin'
pwd = 'admin'
dbname = 'MUDD_V1'

sock_common = xmlrpclib.ServerProxy(host_url + 'common', allow_none=True)
uid = sock_common.login(dbname, user, pwd)
sock = xmlrpclib.ServerProxy(host_url + 'object', allow_none=True)


department = {}
title = {}
employees = {}

def CleanEmployee(e):
    lu = {'Headquarters': 'Cedar Falls',
          'California Branch': 'California',
          'California Branch Office': 'California',
          'Chicago Branch Office': 'Chicago',
          'Tennessee Branch Office': 'Tennessee',
          'NULL': None}
    if e['Location']:
        e['Location'] = lu[e['Location']]

theFile = open(import_file_name, 'rU')
reader = csv.DictReader(theFile)
for row in reader:
    for field in row:
        row[field] = row[field].strip()
        if row[field] == 'NULL':
            row[field] = None
    row['id'] = int(row['id'])
    row['active'] = row['active']

    # cast some fields to the proper type
    row['option_ids'] = row['option_ids']
    for option in row['option_ids']:
        option['id']=option['id']
        option['active']=option['active']
        option['price']=option['price']
        option['cost_price']=option['cost_price']
        option['field_desc']=option['field_desc']
        option['filter_field_id']=option['filter_field_id']
        option['name']=option['name']
        option['value_ref']=option['value_ref']
        option['sales_price']=option['sales_price']


#    if row['Anniversary']:
#        row['Anniversary'] = parser.parse(row['Anniversary']).date().strftime('%m/%d/%Y')
#    row['Birth_Month'] = None
#    row['Birth_Day'] = None
#    if row['Birthday']:
#        row['Birthday'] = parser.parse(row['Birthday']).date().strftime('%m/%d/%Y')
#	row['Birth_Month'] = parser.parse(row['Birthday']).date().month
#	row['Birth_Day'] = parser.parse(row['Birthday']).date().day

    if row['']:
        department[row['Department']] = None

    if row['Title']:
        title[row['Title']] = None

    employees[row['EmpId']] = row
theFile.close()

if do_departments:
    # create the departments
    print '\n\nImporting Departments...'
    for d in department.keys():
        # see if it already exists
        ids = sock.execute(dbname, uid, pwd, 'hr.department', 'search', [('name', '=', d)])
        if ids:
            department[d] = ids[0]
            if update_departments:
                # update it
                values = {
                    'name': d
                }
                print 'updating:', d
                result = sock.execute(dbname, uid, pwd, 'hr.department', 'write', ids, values)
        else:
            # create it
            values = {
                'name': d
            }
            print 'creating:', d
            department_id = sock.execute(dbname, uid, pwd, 'hr.department', 'create', values)
            department[d] = department_id


if do_jobs:
    # create the job positions
    print '\n\nImporting Job Postions...'
    for d in title.keys():
        if d:
            # see if it already exists
            ids = sock.execute(dbname, uid, pwd, 'hr.job', 'search', [('name', '=', d)])
            if ids:
                title[d] = ids[0]
                if update_jobs:
                    # update it
                    values = {
                        'name': d
                    }
                    print 'updating:', d
                    result = sock.execute(dbname, uid, pwd, 'hr.job', 'write', ids, values)
            else:
                # create it
                values = {
                    'name': d
                }
                print 'creating:', d
                job_id = sock.execute(dbname, uid, pwd, 'hr.job', 'create', values)
                title[d] = job_id



if do_employees:
	# create the job positions
	print '\n\nImporting Employees...'
	for k, v in employees.items():
		if v['CurrentlyEmployeed']:
			CleanEmployee(v)
			values = {
				'name': v['FullName'],
				'work_location': v['Location'],
				'work_email': v['Email'],
				'work_phone': v['Phone'],
				'mobile_phone': v['MobilePhone'],
				'birthday': v['Birthday'],
				#'department_id': None,
				#'job_id': None,
				'x_fax': v['Fax'],
				'x_extension': v['Extention'],
				'x_start_date': v['Anniversary'],
				'x_birth_month': v['Birth_Month'],
				'x_birth_day': v['Birth_Day'],
			}
			if do_departments:
				if v['Department']:
					values['department_id'] = department[v['Department']]
			if do_jobs:
				if v['Title']:
					values['job_id'] = title[v['Title']]

			# see if it already exists
			ids = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', [('name', '=', v['FullName'])])
			if ids:
				if update_employees:
					# update it
					print 'updating:', v['FullName']
					result = sock.execute(dbname, uid, pwd, 'hr.employee', 'write', ids, values)
			else:
				# create it
				print 'creating:', v['FullName']
				template_id = sock.execute(dbname, uid, pwd, 'hr.employee', 'create', values)

	# now set their managers
	print '\n\nAssigning Managers...'
	for k, v in employees.items():
		if v['CurrentlyEmployeed']:
			if v['SupervisorId']:
				try:
					ids = sock.execute(dbname, uid, pwd,
						'hr.employee', 'search',
						[('name', '=', employees[v['SupervisorId']]['FullName'])])
				except:
					ids = None
				if ids:
					# update it
					values = {'parent_id': ids[0]}
					print 'updating:', v['FullName'], ids[0]

					# now find the id of the employee
					emp_ids = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', [('name', '=', v['FullName'])])

					result = sock.execute(dbname, uid, pwd, 'hr.employee', 'write', emp_ids, values)


# now clean up all the unused Job Positions
ids = sock.execute(dbname, uid, pwd, 'hr.job', 'search', ['|', ('no_of_employee', '=', 0.0), ('no_of_employee', '=', None)])
result = sock.execute(dbname, uid, pwd, 'hr.job', 'unlink', ids)

# now clean up any unused Departments
ids = sock.execute(dbname, uid, pwd, 'hr.department', 'search', [('member_ids', '=', None)])
result = sock.execute(dbname, uid, pwd, 'hr.department', 'unlink', ids)

# now we have to add them as vendors if they do not already exist in partners
