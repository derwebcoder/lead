#!/usr/bin/python3

import sys
import os
import ast
import docker as d

client = d.from_env(version="1.27")
ll_client = d.APIClient(version="1.27")

def exec_wrapper(container):
    def exec(cmd, shell=None):
        if shell is not None and type(shell) is not str:
            raise Exception("shell has to be a string")
        
        if shell == "bash":
            cmd = "bash -c '" + cmd + "'"

        if shell == "sh":
            cmd = "sh -c '" + cmd + "'"

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

def pull_image(image):
    print("checking if image " + image + " exists...")
    try:
        client.images.get(image)
    except d.errors.ImageNotFound:
        image_repository, image_tag = image.split(':')
        pull_stream = ll_client.pull(image_repository, tag=image_tag, stream=True)
        for line in pull_stream:
            download_status = ast.literal_eval(line.decode('UTF-8'))
            print(download_status.get('id', "unknown id") + " [" + download_status.get('status', "unknown status") + "] " + download_status.get('progress', ""))
        print("Image " + image + " downloaded.")
    else:
        print("Image " + image + " already downloaded.")

def docker(image, mountDocker=False, volumes=None, useHostUser=False):
    def docker_decorator(func):
        def func_wrapper(*kargs, **kwargs):
            pull_image(image)
            container=None
            user=None
            volumesDefault={
                os.getcwd(): {
                    'bind': '/source',
                    'mode': 'rw'
                }
            }
            volumesTotal={}
            volumesTotal.update(volumesDefault)
            if mountDocker is True:
                volumesTotal.update({
                    '/var/run/docker.sock': {
                        'bind': '/var/run/docker.sock',
                        'mode': 'ro'
                    }
                })
            os.path.expanduser("~")
            if isinstance(volumes, dict):
                # Cycling through the volumes to replace dict keys (host path) with absolute path or expanding ~ to user home
                parsedVolumes={}
                for key in volumes:
                    print("replacing " + key)
                    parsedVolumes[os.path.abspath(os.path.expanduser(key))] = volumes[key]
                print(parsedVolumes)
                volumesTotal.update(parsedVolumes)

            if useHostUser is True:
                user=str(os.getuid())+":"+str(os.getgid())

            container = client.containers.run(image, "",
                                            entrypoint="sh -c 'while true; do sleep 1349; done'",
                                            volumes=volumesTotal,
                                            working_dir="/source", 
                                            user=user,
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

def job(name=None, description="No description given."):
    def job_decorator(func):
        print("func")
        dir(func)
        job_name=getattr(func, 'job_name', func.__name__)
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