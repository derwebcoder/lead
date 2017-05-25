import os, sys
from lead.jobs.Job import Job
from lead.helpers.path_helpers import get_cwd, compute_home_directory, compute_absolute_path
from lead.helpers.logging import log, log_error

class DockerJob(Job):

    def __init__(self, name, function, image, **kwargs):
        super().__init__(name, function, **kwargs)

        self.workspace_volume = {
            get_cwd(): {
                'bind': '/source',
                'mode': 'rw'
            }
        }
        self.daemon_volume = {
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'ro'
            }
        }

        self.image = image
        self.volumes = self.__parse_volumes(
            kwargs.get('volumes', []),
            kwargs.get('mount_daemon', False))
        use_host_user = kwargs.get('use_host_user', False)
        self.user = None
        if use_host_user is True:
            self.user = str(os.getuid())+":"+str(os.getgid())


    def run_job(self, *args, **kwargs):
        self.function(exec=self.function, *args, **kwargs)

    def __parse_volumes(self, volumes=None, mount_daemon=False):
        parsed_volumes = {}

        parsed_volumes.update(self.workspace_volume)

        if mount_daemon is True:
            parsed_volumes.update(self.daemon_volume)

        if volumes is None:
            return parsed_volumes

        for item in volumes:
            options = item.split(":")
            host_path = ""
            container_path = ""
            mode = "rw"
            if len(options) < 2 or len(options) > 3:
                log("ERROR | The volume \"" + item + "\" is not a valid volume description. " +
                    "Try <HOST_PATH>:<CONTAINER_PATH>[:ro|rw].")
                sys.exit(8)
            if len(options) >= 2:
                host_path = compute_absolute_path(compute_home_directory(options[0]))
                container_path = options[1]
            if len(options) == 3:
                mode = options[2]

            parsed_volumes[host_path] = {
                'bind': container_path,
                'mode': mode
            }

        return parsed_volumes
