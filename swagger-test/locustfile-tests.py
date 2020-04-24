#!/usr/local/bin/python
import os
from locust import events, TaskSet
from locust.clients import LocustResponse
from requests import Request
from locust.main import load_locustfile
from prance import ResolvingParser
from urllib.parse import urlparse

dir = os.path.dirname(os.path.realpath(__file__))

parser = ResolvingParser(os.path.join(dir, 'swagger.yml'))

locustfile = os.getenv('FILE') or 'locustfile.py'
host = os.getenv('HOST')

if(host is None):
    print("HOST environment variable is not set")
    exit(1)

docstring, locusts = load_locustfile(locustfile)

checked_paths = dict()

for specPath in parser.specification['paths']:
    checked_paths[specPath] = dict()
    for specMethod in parser.specification['paths'][specPath]:
        checked_paths[specPath][specMethod] = False

def validate_spec():
    for specPath in checked_paths:
        for specMethod in checked_paths[specPath]:
            if not checked_paths[specPath][specMethod]:
                print("Route %s with method %s has not been called" % (specPath, specMethod))
                return False
    return True

def validate_request(method, url, **kwargs):
    path = urlparse(url).path

    for specPath in parser.specification['paths']:
        if(specPath.lower() == path.lower()):
            for specMethod in parser.specification['paths'][specPath]:
                if(method.lower() == specMethod.lower()):
                    checked_paths[specPath][specMethod] = True

    r = LocustResponse()
    r.status_code = 200
    r.request = Request(method, url).prepare()

    return r
    
def run_task(taskSet, task):
    print("Checking %s:%s" % (type(taskSet).__name__, task.__name__))

    taskSet.execute_task(task)

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

    taskSet.client._send_request_safe_mode = validate_request

    run_tasks(taskSet)

print("-------------------------------")

if validate_spec():
    exit(0)
else:
    exit(1)