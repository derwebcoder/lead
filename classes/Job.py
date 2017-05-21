
class Job:

    def __init__(self, name, function, **kwargs):
        if name is not None:
            if ' ' in name:
                raise ValueError("A job can not contain a space: \"" + name + "\"")

        if not callable(function):
            raise ValueError("For the job \"" + name + "\" no real function is given.")

        self.name = name
        self.function = function
        self.description = kwargs.get('description', "")

    def run_job(self, *args, **kwargs):
        return self.function(*args, **kwargs)
