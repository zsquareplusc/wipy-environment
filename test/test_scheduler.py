#! /usr/bin/env python3
"""\
Tests for task scheduler.
"""

import os
import sys
import time
import traceback
import threading
import unittest

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../device/flash/lib'))
import scheduler

sys.print_exception = lambda e: traceback.print_tb(e.__traceback__) or print(e)


class TestScheduler(scheduler.Scheduler):
    def __init__(self):
        super().__init__()
        self.low_power = threading.Event()

    def sleep(self):
        print("sleep")
        self.low_power.clear()
        self.low_power.wait()

    def wakeup(self):
        print("wakeup")
        self.low_power.set()



class Test_scheduler(unittest.TestCase):

    def test_basic_run(self):
        s = TestScheduler()
        counter = [0]
        def one():
            yield
            counter[0] += 1
            raise scheduler.ExitScheduler()
        s.run(one)
        self.assertRaises(scheduler.ExitScheduler, s.loop)
        self.assertEqual(counter[0], 1)

    def test_restart(self):
        s = TestScheduler()
        countdown = [2]  # limit restarts to let test finish...
        def failure():
            if countdown[0]:
                countdown[0] -= 1
                yield
                raise Exception("pow!")
            else:
                raise scheduler.ExitScheduler()
        s.run(failure, scheduler.RestartingTask)
        self.assertRaises(scheduler.ExitScheduler, s.loop)
        self.assertEqual(countdown[0], 0)


class Test_scheduler_with_interrupts(unittest.TestCase):

    class InterruptSimulator(threading.Thread):
        """Simulate an interrupt source by using a thread"""
        def __init__(self, scheduler):
            super().__init__()
            self.scheduler = scheduler
            self.flag = self.scheduler.new_flag()
            self.alive = True

        def run(self):
            while self.alive:
                time.sleep(0.1)
                print("irq")
                self.scheduler.set_flag(self.flag)

        def stop(self):
            self.alive = False
            self.join(1)

    def setUp(self):
        """create scheduler and interrupt source"""
        self.scheduler = TestScheduler()
        self.irq_thread = self.InterruptSimulator(self.scheduler)
        self.irq_thread.daemon = True
        self.irq_thread.start()

    def tearDown(self):
        self.irq_thread.stop()

    def test_timer_interrupt(self):
        countdown = [2]  # limit restarts to let test finish...
        def wait_for_timer():
            while True:
                if countdown[0]:
                    print(countdown[0])
                    countdown[0] -= 1
                    yield self.irq_thread.flag
                else:
                    raise scheduler.ExitScheduler()
        self.scheduler.run(wait_for_timer)
        self.assertRaises(scheduler.ExitScheduler, self.scheduler.loop)
        self.assertEqual(countdown[0], 0)




if __name__ == '__main__':
    unittest.main()
