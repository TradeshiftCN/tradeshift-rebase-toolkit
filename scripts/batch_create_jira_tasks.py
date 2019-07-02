#!/usr/bin/env python  
""" 
@author:shz 
@license: Apache Licence 
@file: batch_create_jira_tasks.py 
@time: 2019/03/18
@contact: sunhouzan@163.com
@site:  
@software: PyCharm 
"""
import os

import numpy as np
import pandas as pd
from jira import JIRA

API_TOKEN = 'waHAud0CGc6teFs1d10x63FD'
dir_path = os.path.dirname(os.path.realpath(__file__))
TASK_FILE_PATH = os.path.join(dir_path,'rabase-tasks.csv')

options = {'server': 'https://tradeshift.atlassian.net'}
jira = JIRA(options, basic_auth=('huy@tradeshift.com', API_TOKEN))
members = ['huy', 'lil', 'kimigao', 'mqf', 'cyh', 'lry']
members_dict = {idx: item for idx, item in enumerate(members)}

task_data = pd.read_csv(filepath_or_buffer=TASK_FILE_PATH)
task_data.columns = task_data.columns.str.strip()
task_data = task_data.applymap(lambda x: x.strip() if type(x) is str else x)

task_data['Summary'].str.strip()
task_data['Component/s'].str.strip()
parent_tasks = task_data[task_data['Issue id'].notnull() & (task_data['Issue id']!='')]
parent_tasks['Issue id'] = parent_tasks['Issue id'].astype(str)

subtask_data = task_data[task_data['Parent id'].notnull()]
subtask_data['Parent id'] = subtask_data['Parent id'].astype(str)


mem_index = list(range(len(members)))
# shuffle many times
for i in range(20):
    np.random.shuffle(mem_index)

task_count = len(subtask_data)

task_assignment_list = []
for i in range(task_count):
    sub_idx = i % len(members)
    task_assignment_list.append(members_dict[mem_index[sub_idx]])

cpa_project = jira.project('CPA')
project_comps = jira.project_components(cpa_project)
create_meta = jira.createmeta(projectKeys=['CPA'])
comp_dict = dict()
for comp in project_comps:
    comp_dict[comp.name] = comp.id

sub_task_idx = 0

for idx, parent_task in parent_tasks.iterrows():

    parent_task_dict = parent_task.to_dict()
    local_parent_id = parent_task_dict['Issue id']

    parent_issue = jira.create_issue(project={'key': 'CPA'},
                                     summary=parent_task_dict['Summary'],
                                     issuetype={'name': parent_task_dict['Issue Type']},
                                     description='',
                                     components=[
                                         {
                                             "id": comp_dict[parent_task_dict['Component/s']]
                                         }
                                     ],
                                     assignee={'name': parent_task_dict['Assignee']},
                                     reporter={'name': parent_task_dict['Reporter']},
                                     priority={'name': parent_task_dict['Priority']}
                                     # customfield_10008=parent_task_dict['Custom field (Story Points)']
                                     )
    # parent_issue.update(customfield_10008=parent_task_dict['Custom field (Story Points)'])
    print(f'{parent_issue.key} is created')
    for sub_idx, sub_task in subtask_data[subtask_data['Parent id'] == local_parent_id].iterrows():
        sub_task_dict = sub_task.to_dict()
        sub_issue = jira.create_issue(project={'key': 'CPA'},
                                      parent={'id': parent_issue.id},
                                      summary=sub_task_dict['Summary'],
                                      issuetype={'name': sub_task_dict['Issue Type']},
                                      description='',
                                      components=[
                                          {
                                              "id": comp_dict[sub_task_dict['Component/s']]
                                          }
                                      ],
                                      assignee={'name': sub_task_dict['Assignee']},
                                      reporter={'name': sub_task_dict['Reporter']},
                                      priority={'name': sub_task_dict['Priority']}
                                      # customfield_10008=parent_task_dict['Custom field (Story Points)']
                                      )
        sub_task_idx += 1
        print(f'{sub_issue.key} is created')
