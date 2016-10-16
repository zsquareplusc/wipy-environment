#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
A simple scheduler based on generators.
"""
import gc
import sys
import time


class ExitScheduler(Exception):
    pass


class Task(object):
    def __init__(self, scheduler, generator):
        self.scheduler = scheduler
        self.generator = generator
        self.iterator = generator()
        self.mask = 0

    def stop(self):
        self.scheduler.remove(self)

    def restart(self):
        self.scheduler.remove(self)
        self.iterator = self.generator()
        self.scheduler.running.append(self)

    def handle_exception(self, exception):
        sys.print_exception(exception)


class RestartingTask(Task):
    def handle_exception(self, exception):
        sys.print_exception(exception)
        self.restart()


class Scheduler(object):
    def __init__(self):
        self.running = []
        self.waiting = []
        self.flags = 0
        self.flag_counter = 0

    def clear(self):
        del self.running[:]
        del self.waiting[:]

    def new_flag(self):
        flag = 1 << self.flag_counter
        self.flag_counter += 1
        return flag

    def run(self, generator, cls=Task):
        task = cls(self, generator)
        self.running.append(task)
        return task

    def remove(self, task):
        if task in self.running:
            self.running.remove(task)
        if task in self.waiting:
            self.waiting.remove(task)

    def set_flag(self, flag):
        self.flags |= flag
        self.wakeup()

    def loop(self):
        while True:
            #~ print("..sched")
            if self.flags:
                for task in list(self.waiting):
                    if self.flags & task.mask:
                        self.running.append(task)
                        self.waiting.remove(task)
                self.flags = 0
            if self.running:
                for task in list(self.running):
                    try:
                        #~ print("! next->{}".format(task.generator.__name__))
                        mask = task.iterator.__next__()
                    except StopIteration:
                        self.remove(task)
                    except ExitScheduler:
                        raise
                    except:
                        # other errors: remove task, handle exception
                        self.remove(task)
                        task.handle_exception(sys.exc_info()[1])
                    else:
                        if mask:
                            self.running.remove(task)
                            self.waiting.append(task)
                            task.mask = mask
            else:
                self.sleep()

    def wakeup(self):
        pass

    def sleep(self):
        # XXX use low power features, e.g. machine.idle()
        time.sleep_ms(10)
        gc.collect()

