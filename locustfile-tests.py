#!/usr/local/bin/python

import os
from locust import events, TaskSet
from locust.main import load_locustfile

locustfile = os.getenv('FILE') or 'locustfile.py'
host = os.getenv('HOST')

if(host is None):
    print("HOST environment variable is not set")
    exit(1)

docstring, locusts = load_locustfile(locustfile)

total_result = True
request_result = None
request_exception = None

def request_success(request_type, name, response_time, response_length, **kw):
    global request_result
    print("Request succeeded: %s, %s" % (request_type, name))
    request_result = True

def request_failure(request_type, name, response_time, response_length, exception, **kw):
    global request_result
    global request_exception
    print("Request failed: %s, %s" % (request_type, name))
    request_result = False
    request_exception = exception

events.request_success += request_success
events.request_failure += request_failure

def run_task(taskSet, task):
    global request_result
    global request_exception
    global total_result
    print("\n-----------------------\nRunning test for %s:%s\n-----------------------" % (type(taskSet).__name__, task.__name__))
    request_result = None
    request_exception = None

    taskSet.execute_task(task)

    if request_result is None:
        print("No request was made")
    
    if request_result != True:
        total_result = False

    if request_exception is not None:
        print("Failed with exception: %s" % request_exception)

def run_tasks(taskSet):
    for task in taskSet.tasks:
        if hasattr(task, "tasks") and issubclass(task, TaskSet):
            run_tasks(task(taskSet))
        else:
            run_task(taskSet, task)

for locust in locusts.values():
    locust.host = host

    user = locust()

    taskSet = user.task_set(user)

    run_tasks(taskSet)

if total_result:
    exit(0)
else:
    exit(1)