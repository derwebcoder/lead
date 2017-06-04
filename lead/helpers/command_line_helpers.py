import sys
import signal
from lead.helpers.logging import log_error
from lead.helpers.DockerHelper import DockerHelper

dockerHelper = DockerHelper()

def clean_arguments(cli_input):
    args = list()
    opts = dict()
    vals = dict()

    # print("##### ARGS")
    for index, k in enumerate(cli_input):
        # print(index, k)

        if k.startswith('--'):
            if k == '--exec':
                log_error("You can not use value name \"exec\": \"" +
                          k + "\" is violating this rule.")
                sys.exit(8)
            if '=' in k:
                key, val = k.split('=')
            else:
                key, val = k, 'true'
            vals[key.strip('--')] = val
        elif k.startswith('-'):
            if '=' in k:
                key, val = k.split('=')
            else:
                key, val = k, 'true'
            opts[key.strip('-')] = val
        else:
            args.append(k)

    # print("##### ARGS")
    return args, opts, vals

def signal_handler(rec_signal, frame):
    print()
    print("====== Received signal " + str(rec_signal))
    print("==== Stopping pipeline")
    print("==== Stopping and removing containers")
    dockerHelper.kill_all_container()
    print("==== Ending lead with error 1")
    sys.exit(1)

def register_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

