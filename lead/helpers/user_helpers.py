import glob
import sys
from lead.helpers.logging import log_error
from lead.helpers.DockerHelper import DockerHelper

dockerHelper = DockerHelper()

def is_container_running_with_id(id=None):
    return DockerHelper.is_container_running_with_id(id)

def fileExists(pattern=None):
    return glob.glob(pattern)

def depends(jobName=None, ifTrue=True, ifFalse=False):
    if callable(jobName):
        if ifTrue and not ifFalse:
            jobName()
    else:
        log_error("depends() \"" + jobName + "\" is not a function.")
        sys.exit(16)