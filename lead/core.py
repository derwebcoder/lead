
import sys
from lead.helpers.logging import log, log_error
from lead.helpers.command_line_helpers import clean_arguments, register_signal_handler
from lead.helpers.path_helpers import check_if_file_exists
from lead.pipeline.Pipeline import Pipeline
from lead.decorator.docker import docker
from lead.decorator.job import job
from lead.helpers.user_helpers import is_container_running_with_id, file_exists, depends

VERSION = '1.0.0'
HELP_MESSAGE = """\
General usage:

    lead [-<option>[=<value>] ...] [<job> ...] [--<variable>[=<value>] ...]

    <option>:

        pipeline=<Path_To_Pipeline_File>    Will load the given pipeline for the current directory
        debug                               Shows additional information while running your pipeline
        dry                                 Does not really execute the jobs but show what would happen

    <job>:

        This has to be a declared job inside your pipeline file. Either the function name or the name
        specified inside of @job. You can pass in more than one job. The execution happens in the
        given order.

    <variable>:

        This can be job-specific variables you need for your jobs.


Lead specific commands:

    lead <command>

    <command>:
    
        help        Prints this help message
        version     Prints the current version
        info        Prints general information about the pipeline. Default if no <job> is given (!)
"""
DEFAULT_PIPELINE_FILE = "pipeline.py"

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

    args, opts, vals = clean_arguments(sys.argv[1:])

    if len(args) == 1:
        arg = args[0]
        if arg == "help":
            log("Lead help")
            print(HELP_MESSAGE)
            sys.exit(0)
        elif arg == "version":
            log("Lead Version " + VERSION)
            sys.exit(0)

    pipeline_file = opts.get("pipeline", DEFAULT_PIPELINE_FILE)
    if not check_if_file_exists(pipeline_file):
        log_error("""Could not find a pipeline.
        Looked for '""" + pipeline_file + """' but this file does not exist.""")
        sys.exit(1)

    exec(compile(open(pipeline_file, "rb").read(), pipeline_file, 'exec'))

    if len(args) == 1:
        arg = args[0]
        if arg == "info":
            log("Showing general information about the pipeline")
            print()
            pipeline.show_information()
            sys.exit(0)

    if len(args) == 0:
        log("Showing general information about the pipeline")
        print()
        pipeline.show_information()
        sys.exit(0)

    pipeline.run_jobs(args, vals)





