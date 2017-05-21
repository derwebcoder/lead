
from classes.DockerJob import DockerJob

def docker(image, mount_daemon=False, volumes=None, use_host_user=True):
    def docker_decorator(func):

        job = DockerJob(
            name=func.__name__,
            function=func,
            image=image,
            volumes=volumes,
            mount_daemon=mount_daemon,
            use_host_user=use_host_user)

        def func_wrapper(*args, **kwargs):
            return job.run_job(*args, **kwargs)

        func_wrapper.job = job

        return func_wrapper
    return docker_decorator
