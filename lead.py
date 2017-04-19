#!/usr/bin/python3

import sys
import os
import docker as d

client = d.from_env(version="1.27")
ll_client = d.APIClient(version="1.27")

def exec_wrapper(container):
    def exec(cmd, shell=None):
        if type(shell) is not str:
            raise Exception("shell has to be a string")
        
        if shell == "bash":
            cmd = "bash -c '" + cmd + "'"

        print("exec " + cmd + " in " + container.id)

        exec_id = ll_client.exec_create(container.id, cmd)['Id']
        exec_stream = ll_client.exec_start(exec_id, detach=False, stream=True)

        output = ""

        for line in exec_stream:
            print(line.decode('UTF-8'))
            output = output + line.decode('UTF-8')

        exec_result = ll_client.exec_inspect(exec_id)
        
        return exec_result['ExitCode'], output
    
    return exec

def docker(image):
    def docker_decorator(func):
        def func_wrapper(*kargs, **kwargs):
            container = client.containers.run(image, "", 
                entrypoint="sleep infinity",
                volumes={os.getcwd(): {'bind':'/source', 'mode':'rw'}},
                working_dir="/source",
                user=str(os.getuid())+":"+str(os.getgid()),
                detach=True)
            print("Container started")
            exec_func = exec_wrapper(container)
            print("Exec Func:")
            print(exec_func)
            func(*kargs, exec=exec_func, **kwargs)
            container.kill()
            container.remove(force=True)
        func_wrapper.job_name = func.__name__
        return func_wrapper
    return docker_decorator

job_dict = dict()

def job(name=None, description="unknown"):
    def job_decorator(func):
        print("func")
        dir(func)
        job_name=func.job_name
        if name is not None:
            if ' ' in name:
                raise ValueError("Ein Job Name darf kein Leerzeichen enthalten: " + name)
            job_name=name
        job_dict[job_name] = func
        def func_wrapper(*kargs, **kwargs):
            print("kargs: ")
            print(kargs)
            print("kwargs: ")
            print(kwargs)
            func(*kargs, **kwargs)
        return func_wrapper
    return job_decorator

exec(compile(open("pipeline.py", "rb").read(), "pipeline.py", 'exec'))

def clean_arguments(args):
    ret_jobs = list()
    ret_args = dict()

    print("##### ARGS")
    for index, k in enumerate(args):
        print(index, k)

        if k.startswith('--'):
            if '=' in k:
                key, val = k.split('=')
            else:
                key, val = k, 'true'
            ret_args[key.strip('--')] = val
        else:
            ret_jobs.append(k)

    print(ret_jobs)
    print(ret_args)
    print("##### ARGS")
    return ret_jobs, ret_args

jobs_arg, opt_arg = clean_arguments(sys.argv[1:])

def pre_check(jobs_arg, job_dict):
    for job in jobs_arg:
        if job not in job_dict:
            print("nicht vorhanden")
        else:
            print("vorhanden")

pre_check(jobs_arg, job_dict)

for job in jobs_arg:
    job_dict[job]()

print(job_dict)