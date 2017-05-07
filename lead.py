#!/usr/bin/python3

########################################
#
# This is a proof of concept. This code is neither good nor commented.
#
########################################

import sys
import signal
import os
import ast
import docker as d
import configparser
import glob

def getcwd():
    return os.environ.get("CWD", os.getcwd())

def computeHomeDirectory(path=""):
    # print("cHD path: " + path)
    home=os.environ.get("HOME", os.path.expanduser("~"))
    
    # print("cHD HOME: " + home)
    home_replaced=path.replace("~",home,1)
    # print("cHD repl: " + home_replaced)
    return path if home_replaced == "" else home_replaced

def computeAbsolutePath(path=""):
    if not path.startswith("."):
        return path
    if path == "." or path == "./":
        return getcwd()

    cwd=getcwd()
    path_current=path
    # print("path_current: " + path_current)
    nr_parent_dirs=path_current.count("../")
    # print("nr_parent_dirs: " + str(nr_parent_dirs))
    nr_dirs_cwd=cwd.count("/")
    # print("nr_dirs_cwd: " + str(nr_dirs_cwd))

    if nr_parent_dirs > nr_dirs_cwd:
        print("Error: Invalid path '" + path + "' for current working directory '" + cwd + "'.")
        sys.exit(1)

    cwd_slash_positions=( [pos for pos, char in enumerate(cwd) if char == "/"])
    # print("cwd_slash_positions: ")
    # print(cwd_slash_positions)
    cwd_cut=cwd[:(cwd_slash_positions[nr_dirs_cwd - nr_parent_dirs])+1]
    # print("cwd_cut: " + cwd_cut)

    path_without_parents=path.replace("../", "")
    path_without_relative_path=path_without_parents.replace("./", "")

    # print("cAP path: "  + path)
    cwd=getcwd()
    # print("cAP cwd : "  + cwd)
    absolute_path=cwd_cut + path_without_relative_path
    # print("cAP abso: " + absolute_path)
    return absolute_path

lead_settings_path=computeHomeDirectory("~") + "/.lead/lead.settings.ini"
print("# Loading Lead settings from " + lead_settings_path)
config=configparser.ConfigParser()
lead_settings=None
try:
    config.read(lead_settings_path)
    lead_settings = config['Docker']
except BaseException as exc:
    print("# Lead settings file not found. Using default values.")
    lead_settings={}

client=None
ll_client=None
docker_api_version=lead_settings.get("docker-api-version")
if docker_api_version is not None:
    client = d.from_env(version=docker_api_version)
    ll_client = d.APIClient(version=docker_api_version)
else:
    client = d.from_env(version="auto")
    ll_client = d.APIClient(version="auto")

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

        # print()
        # print("***")
        # print("DEBUG | ")
        # print("exec " + cmd + " in " + container.id)
        # print()
        # print("***")
        # print()

        exec_id = ll_client.exec_create(container.id, cmd)['Id']
        exec_stream = ll_client.exec_start(exec_id, detach=False, stream=True)

        output = ""
        print()
        print("*** CONTAINER OUTPUT")
        print()
        for line in exec_stream:
            print(line.decode('UTF-8'))
            output = output + line.decode('UTF-8')
        print("*** END OF OUTPUT")

        exec_result = ll_client.exec_inspect(exec_id)
        
        return exec_result['ExitCode'], output
    
    return exec

def pull_image(image):
    # print("checking if image " + image + " exists...")
    try:
        client.images.get(image)
    except d.errors.ImageNotFound:
        print("INFO | Image \"" + image + "\" not found. Pulling ...")
        image_repository, image_tag = image.split(':')
        pull_stream = ll_client.pull(image_repository, tag=image_tag, stream=True)
        for line in pull_stream:
            download_status = ast.literal_eval(line.decode('UTF-8'))
            print(download_status.get('id', "unknown id") + " [" + download_status.get('status', "unknown status") + "] " + download_status.get('progress', ""))
        print("INFO | Image " + image + " successfully downloaded.")
    # else:
        # print("Image " + image + " already downloaded.")

containers=[]
def docker(image, mountDaemon=False, volumes=None, useHostUser=True):
    def docker_decorator(func):
        def func_wrapper(*kargs, **kwargs):
            pull_image(image)
            container=None
            user=None
            # print("**************************************************")
            # print(os.getcwd())
            # print("**************************************************")
            volumesDefault={
                getcwd(): {
                    'bind': '/source',
                    'mode': 'rw'
                }
            }
            volumesTotal={}
            volumesTotal.update(volumesDefault)
            if mountDaemon is True:
                volumesTotal.update({
                    '/var/run/docker.sock': {
                        'bind': '/var/run/docker.sock',
                        'mode': 'ro'
                    }
                })
            os.path.expanduser("~")
            if isinstance(volumes, list):
                # Cycling through the volumes to replace dict keys (host path) with absolute path or expanding ~ to user home
                parsedVolumes={}
                for item in volumes:
                    options = item.split(":")
                    host_path=""
                    container_path=""
                    mode="rw"
                    if len(options) < 2 or len(options) > 3:
                        print()
                        print("==============================")
                        print()
                        print("ERROR | The volume \"" + item + "\" is not a valid volume description. Try <HOST_PATH>:<CONTAINER_PATH>[:ro|rw].")
                        print()
                        print("==============================")
                        sys.exit(8)
                    if len(options) >= 2:
                        host_path=computeAbsolutePath(computeHomeDirectory(options[0]))
                        container_path=options[1]
                    if len(options) == 3:
                        mode=options[2]

                    parsedVolumes[host_path] = {
                        'bind': container_path,
                        'mode': mode
                    }

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
            # print("Container started")
            exec_func = exec_wrapper(container)
            # print("Exec Func:")
            # print(exec_func)
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
        # print("func")
        dir(func)
        job_name=getattr(func, 'job_name', func.__name__)
        if name is not None:
            if ' ' in name:
                raise ValueError("Ein Job Name darf kein Leerzeichen enthalten: " + name)
            job_name=name
        job_dict[job_name] = func
        def func_wrapper(*kargs, **kwargs):
            # print("kargs: ")
            # print(kargs)
            # print("kwargs: ")
            # print(kwargs)
            return func(*kargs, **kwargs)
        #job_dict[job_name] = func_wrapper
        return func_wrapper
    return job_decorator

exec(compile(open("pipeline.py", "rb").read(), "pipeline.py", 'exec'))

def clean_arguments(args):
    ret_jobs = list()
    ret_args = dict()

    # print("##### ARGS")
    for index, k in enumerate(args):
        # print(index, k)

        if k.startswith('--'):
            if k == '--exec':
                print()
                print("==============================")
                print()
                print("ERROR | You can not use option name \"exec\": \"" + job + "\" is violating this rule.")
                print()
                print("==============================")
                sys.exit(8)
            if '=' in k:
                key, val = k.split('=')
            else:
                key, val = k, 'true'
            ret_args[key.strip('--')] = val
        else:
            ret_jobs.append(k)

    # print(ret_jobs)
    # print(ret_args)
    # print("##### ARGS")
    return ret_jobs, ret_args

jobs_arg, opt_arg = clean_arguments(sys.argv[1:])

def pre_check(jobs_arg, job_dict):
    for job in jobs_arg:
        if job not in job_dict:
            print()
            print("==============================")
            print()
            print("ERROR | Could not find a job with the name \"" + job + "\" in pipeline.py.")
            print()
            print("==============================")
            sys.exit(6)

pre_check(jobs_arg, job_dict)

def isContainerRunningWithId(id=None):
    try:
        client.containers.get(id)
        return True
    except BaseException:
        return False

def fileExists(pattern=None):
    return glob.glob(pattern)

def depends(jobName=None, ifTrue=True, ifFalse=False):
    if callable(jobName):
        if ifTrue and not ifFalse:
            jobName()
    else:
        print()
        print("==============================")
        print()
        print("ERROR | depends() + \"" + jobName + "\" is not a function.")
        print()
        print("==============================")
        sys.exit(16)

for job in jobs_arg:
    print()
    print("==============================")
    print()
    print("INFO | Running " + job)
    print()
    print("==============================")
    print()
    return_value=job_dict[job](**opt_arg)
    if return_value is not None:
        if type(return_value) is not int:
            print()
            print("=========================")
            print()
            print("ERROR | The job \"" + job + "\" returned \"" + str(return_value) + "\".")
            print("ERROR | Failing pipeline because of non zero return value.")
            print()
            print("=========================")
            remove_all_containers()
            sys.exit(2)
        else:
            if return_value > 0:
                print()
                print("=========================")
                print()
                print("ERROR | The job \"" + job + "\" returned \"" + str(return_value) + "\".")
                print("ERROR | Failing pipeline because of non zero return value.")
                print()
                print("=========================")
                remove_all_containers()
                sys.exit(return_value)
    

print()
print("==============================")
print()
print("Pipeline ended successfully. :)")
print()
print("==============================")