
import sys
from lead.helpers.logging import log_error

class Pipeline:

    def __init__(self):
        self.jobs = dict()

    def add_job(self, job):
        self.jobs[job.get_name()] = job

    def __pre_check(self, jobs):
        for job in jobs:
            if job not in self.jobs:
                log_error("Could not find a job with the name \"" + job + "\" in pipeline.py.")
                sys.exit(6)

    def run_jobs(self, jobs, args):
        self.__pre_check(jobs)
        for job in jobs:
            real_job = self.jobs.get(job)
            real_job.run(**args)