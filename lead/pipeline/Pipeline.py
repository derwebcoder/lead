
import sys
from lead.helpers.logging import log_error

class Pipeline:

    __jobs = None

    def __init__(self):
        if Pipeline.__jobs is None:
            Pipeline.__jobs = dict()

    def add_job(self, job):
        Pipeline.__jobs[job.get_name()] = job

    def __pre_check(self, jobs):
        for job in jobs:
            if job not in Pipeline.__jobs:
                log_error("Could not find a job with the name \"" + job + "\" in pipeline.py.")
                sys.exit(6)

    def run_jobs(self, jobs, args):
        self.__pre_check(jobs)
        for job in jobs:
            real_job = Pipeline.__jobs.get(job)
            real_job.run(**args)

    def show_information(self):
        for job_name, job in Pipeline.__jobs.items():
            print(job.get_name())
            print("\t" + job.get_description())
