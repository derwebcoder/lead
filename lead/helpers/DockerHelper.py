
from lead.helpers.logging import log, log_error
from lead.stores.ContainerStore import ContainerStore
import docker as d
import ast

class DockerHelper:

    __store = ContainerStore()

    def __init__(self):
        self.client = None
        self.ll_client = None
        # docker_api_version=lead_settings.get("docker-api-version")
        docker_api_version = None
        if docker_api_version is not None:
            client = d.from_env(version=docker_api_version)
            ll_client = d.APIClient(version=docker_api_version)
        else:
            client = d.from_env(version="auto")
            ll_client = d.APIClient(version="auto")

    def create_container(self, image, volumes=None, user=None):
        container = self.client.containers.run(
            image,
            "", # CMD not necessary because of entrypoint
            entrypoint="sh -c 'while true; do sleep 1349; done'",
            volumes=volumes,
            working_dir="/source",
            user=user,
            detach=True)
        DockerHelper.__store.add_container(container)
        return container

    def kill_container(self, container):
        container.kill()
        container.remove(force=True)
        DockerHelper.__store.remove_container(container)

    def kill_all_container(self):
        for container in DockerHelper.__store.get_containers():
            self.kill_container(container)

    def create_exec(self, container):
        def exec(cmd, shell=None):
            #if dry_run:
            #    return 0, "Success"
            
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

            exec_id = self.ll_client.exec_create(container.id, cmd)['Id']
            exec_stream = self.ll_client.exec_start(exec_id, detach=False, stream=True)

            output = ""
            log("*** CONTAINER OUTPUT")
            for line in exec_stream:
                line_decoded = line.decode('UTF-8')
                lines = line_decoded.splitlines()
                for output_line in lines:
                    print("[log] " + output_line)
                output = output + line_decoded

            exec_result = self.ll_client.exec_inspect(exec_id)
            
            return exec_result['ExitCode'], output
        
        return exec
    
    def check_for_image(self, image):
        try:
            self.client.images.get(image)
        except d.errors.ImageNotFound:
            log("Image \"" + image + "\" not found. Pulling ...")
            self.__pull_image(image)
            log("Image " + image + " successfully downloaded.")

    def is_container_running_with_id(self, id=None):
        try:
            self.client.containers.get(id)
            return True
        except BaseException:
            return False 

    def __pull_image(self, image):
        image_repository, image_tag = image.split(':')
        if image_tag is None:
            image_tag = "latest"
        pull_stream = self.ll_client.pull(image_repository, tag=image_tag, stream=True)
        for line in pull_stream:
            download_status = ast.literal_eval(line.decode('UTF-8'))
            log(download_status.get('id', "unknown id") +
                " [" + download_status.get('status', "unknown status") + "] " +
                download_status.get('progress', ""))
