import sys
import signal
from lead.helpers.logging import log_error
from lead.helpers.DockerHelper import DockerHelper

dockerHelper = DockerHelper()

def clean_arguments(args):
    ret_jobs = list()
    ret_args = dict()

    # print("##### ARGS")
    for index, k in enumerate(args):
        # print(index, k)

        if k.startswith('--'):
            if k == '--exec':
                log_error("You can not use option name \"exec\": \"" + k + "\" is violating this rule.")
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
    if 'dry-run' in ret_args:
        dry_run = True
    # print("##### ARGS")
    return ret_jobs, ret_args

def signal_handler(signal, frame):
    print()
    print("====== Received signal " + str(signal))
    print("==== Stopping pipeline")
    print("==== Stopping and removing containers")
    dockerHelper.kill_all_container()
    print("==== Ending lead with error 1")
    sys.exit(1)

def register_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

