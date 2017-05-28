
from lead.jobs.Job import Job

def job(name=None, description=None):
    def job_decorator(func):

        job_obj = None

        if hasattr(func, 'job'): # Ture if @docker has been used
            job_obj = getattr(func, 'job')
            if name is not None:
                job_obj.name = name
        else:
            job_obj = Job(
                name=name or func.__name__,
                function=func,
                description=description)

        def func_wrapper(*args, **kwargs):
            return job_obj.run(*args, **kwargs)

        return func_wrapper
    return job_decorator