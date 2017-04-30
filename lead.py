#!/usr/bin/python3

import sys
import signal
import os
import ast
import docker as d

client = d.from_env(version="1.27")
ll_client = d.APIClient(version="1.27")

def signal_handler(signal, frame):
    print()
    print("====== Received signal " + str(signal))
    print("==== Stopping pipeline")
    print("==== Stopping and removing containers")
    remove_all_containers()
    print("==== Ending lead with error 1")
    sys.exit(1)

def remove_all_containers():
    for container in containers:
        container.kill()
        container.remove(force=True)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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

def getcwd():
    return os.environ.get("CWD", os.getcwd())

def computeHomeDirectory(path=""):
    print("cHD path: " + path)
    home=os.environ.get("HOME", os.path.expanduser("~"))
    
    print("cHD HOME: " + home)
    home_replaced=path.replace("~",home,1)
    print("cHD repl: " + home_replaced)
    return path if home_replaced == "" else home_replaced

def computeAbsolutePath(path=""):
    if not path.startswith("."):
        return path
    if path == "." or path == "./":
        return getcwd()

    cwd=getcwd()
    path_current=path
    print("path_current: " + path_current)
    nr_parent_dirs=path_current.count("../")
    print("nr_parent_dirs: " + str(nr_parent_dirs))
    nr_dirs_cwd=cwd.count("/")
    print("nr_dirs_cwd: " + str(nr_dirs_cwd))

    if nr_parent_dirs > nr_dirs_cwd:
        print("Error: Invalid path '" + path + "' for current working directory '" + cwd + "'.")
        sys.exit(1)

    cwd_slash_positions=( [pos for pos, char in enumerate(cwd) if char == "/"])
    print("cwd_slash_positions: ")
    print(cwd_slash_positions)
    cwd_cut=cwd[:(cwd_slash_positions[nr_dirs_cwd - nr_parent_dirs])+1]
    print("cwd_cut: " + cwd_cut)

    path_without_parents=path.replace("../", "")
    path_without_relative_path=path_without_parents.replace("./", "")

    print("cAP path: "  + path)
    cwd=getcwd()
    print("cAP cwd : "  + cwd)
    absolute_path=cwd_cut + path_without_relative_path
    print("cAP abso: " + absolute_path)
    return absolute_path

containers=[]
def docker(image, mountDocker=False, volumes=None, useHostUser=True):
    def docker_decorator(func):
        def func_wrapper(*kargs, **kwargs):
            pull_image(image)
            container=None
            user=None
            print("**************************************************")
            print(os.getcwd())
            print("**************************************************")
            volumesDefault={
                getcwd(): {
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
                    computed_volume = computeAbsolutePath(computeHomeDirectory(key))
                    print("computed "  + computed_volume)
                    parsedVolumes[computed_volume] = volumes[key]
                    #parsedVolumes[os.path.abspath(os.path.expanduser(key))] = volumes[key]
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
            containers.append(container)
            print("Container started")
            exec_func = exec_wrapper(container)
            print("Exec Func:")
            print(exec_func)
            return_value=func(*kargs, exec=exec_func, **kwargs)
            container.kill()
            container.remove(force=True)
            containers.remove(container)
            return return_value

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
            return func(*kargs, **kwargs)
        #job_dict[job_name] = func_wrapper
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
    return_value=job_dict[job]()
    if return_value is not None:
        if type(return_value) is not int:
            print("The job \"" + job + "\" returned \"" + str(return_value) + "\".")
            print("Failing pipeline because of non zero return value.")
            remove_all_containers()
            sys.exit(2)
        else:
            if return_value > 0:
                print("The job \"" + job + "\" returned \"" + str(return_value) + "\".")
                remove_all_containers()
                sys.exit(return_value)

print(job_dict)