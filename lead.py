#!/usr/bin/python3

import sys
import docker as d

client = d.from_env(version="1.27")
ll_client = d.APIClient(version="1.27")

def exec_wrapper(container):
    def exec(cmd):
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
        container = client.containers.run(image, "sleep infinity", detach=True)
        def func_wrapper(*kargs, **kwargs):
            exec_func = exec_wrapper(container)
            print("Exec Func:")
            print(exec_func)
            func(*kargs, exec=exec_func, **kwargs)
            container.kill()
            container.remove(force=True)
        return func_wrapper
    return docker_decorator

job_dict = dict()

def job(name="unknown", description="unknown"):
    def job_decorator(func):
        if ' ' in name:
            raise ValueError("Ein Job Name darf kein Leerzeichen enthalten: " + name)
        job_dict[name] = func
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