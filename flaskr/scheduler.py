""" This file stores a scheduler instance """

import sched
import time

# create a shared insance of the scheduler
SCHEDULER = sched.scheduler(time.time, time.sleep)
