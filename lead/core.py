
import sys
from lead.decorator.docker import docker
from lead.decorator.job import job
from lead.helpers.logging import log
from lead.helpers.command_line_helpers import clean_arguments, register_signal_handler
from lead.pipeline.Pipeline import Pipeline
from lead.helpers.user_helpers import is_container_running_with_id, file_exists, depends

def init():
    register_signal_handler()
    #lead_settings_path=computeHomeDirectory("~") + "/.lead/lead.settings.ini"
    #print("# Loading Lead settings from " + lead_settings_path)
    #config=configparser.ConfigParser()
    #lead_settings=None
    #try:
    #    config.read(lead_settings_path)
    #    lead_settings = config['Docker']
    #except BaseException as exc:
    #    print("# Lead settings file not found. Using default values.")
    #    lead_settings={}
    pipeline = Pipeline()

    exec(compile(open("pipeline.py", "rb").read(), "pipeline.py", 'exec'))

    jobs_arg, opt_arg = clean_arguments(sys.argv[1:])
    pipeline.run_jobs(jobs_arg, opt_arg)





