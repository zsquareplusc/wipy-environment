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
import time


class Task:
    def __init__(self, generator):
        self.mask = 0
        self.generator = generator


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

    def run(self, generator):
        self.running.append(Task(generator()))

    def remove(self, task):
        if task in self.running:
            self.running.remove(task)
        if task in self.waiting:
            self.waiting.remove(task)

    def set_flag(self, flag):
        self.flags |= flag
        # XXX wakeup

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
                        mask = task.generator.__next__()
                    except StopIteration:
                        self.remove(task)
                    # XXX "except" other errors: remove task too, print exception, restart option?
                    else:
                        if mask:
                            self.running.remove(task)
                            self.waiting.append(task)
                            task.mask = mask
            else:
                # XXX sleep
                time.sleep_ms(10)
                gc.collect()

