#!/usr/bin/python3

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
            func(*kargs, exec=exec_wrapper(container), **kwargs)
            container.kill()
            container.remove(force=True)
        return func_wrapper
    return docker_decorator

job_dict = dict()

def job(name):
    def job_decorator(func):
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

test("Ivana", "22")

print(job_dict)