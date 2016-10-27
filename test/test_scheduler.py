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


class Stopwatch(object):
    def __init__(self):
        self.t_start = None
        self.t_end = None
        self.laps = []

    def __enter__(self):
        self.t_start = time.time()

    def __exit__(self, *args):
        self.t_end = time.time()
        self.laps.append(self.t_end - self.t_start)

    @property
    def elapsed_time(self):
        return sum(self.laps)


class abort(object):
    """helper class (can beused as task) to abort the scheduler loop"""
    def __next__(self):
        raise scheduler.ExitScheduler()


class TestScheduler(scheduler.Scheduler):
    def __init__(self):
        super().__init__()
        self.low_power = threading.Event()
        self.history = []

    def trace(self, event):
        # print(event)
        self.history.append(event)

    def sleep(self):
        self.trace("sleep")
        self.low_power.clear()
        self.low_power.wait()

    def wakeup(self):
        self.trace("wakeup")
        self.low_power.set()

    def set_flag(self, flag):
        self.trace("set_flag")
        super().set_flag(flag)

    def run_loop(self, timeout=3):

        def run_abort():
            self.trace('abort')
            self.run(abort)

        timeout = threading.Timer(timeout, run_abort)
        timeout.start()
        self.loop()
        timeout.cancel()


class Test_scheduler_test_infrastructure(unittest.TestCase):
    """Test for the helper code in this module"""

    def test_abort(self):
        """The TestScheduler automatically terminates the loop"""
        s = TestScheduler()
        t_start = time.time()
        self.assertRaises(scheduler.ExitScheduler, s.run_loop)
        t_end = time.time()
        run_time = t_end - t_start
        self.assertTrue(2.9 < run_time < 4)


class Test_scheduler(unittest.TestCase):

    def test_sleep(self):
        """If there is no task, it goes to sleep"""
        s = TestScheduler()
        self.assertRaises(scheduler.ExitScheduler, s.run_loop, 1)
        self.assertEqual(s.history, ['sleep', 'abort', 'wakeup'])

    def test_basic_run(self):
        """Tasks can be started with run"""
        s = TestScheduler()
        counter = [0]
        def one():
            yield
            counter[0] += 1
            raise scheduler.ExitScheduler()
        s.run(one)
        self.assertRaises(scheduler.ExitScheduler, s.run_loop)
        self.assertEqual(counter[0], 1)

    def test_restart(self):
        """Tasks can be restared after errors"""
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
        self.assertRaises(scheduler.ExitScheduler, s.run_loop)
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
                self.scheduler.trace("irq")
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
        """Intterups can wake up the scheduler"""
        countdown = [2]  # limit restarts to let test finish...
        def wait_for_timer():
            while True:
                if countdown[0]:
                    #~ print(countdown[0])
                    countdown[0] -= 1
                    yield self.irq_thread.flag
                else:
                    raise scheduler.ExitScheduler()
        self.scheduler.run(wait_for_timer)
        self.assertRaises(scheduler.ExitScheduler, self.scheduler.run_loop)
        self.assertEqual(countdown[0], 0)

    def test_delay(self):
        """Delays have to be implemented by waiting on flags"""
        stopwatch = Stopwatch()

        def sleep(n):
            for i in range(int(n*10)):  # irq at 0.1 sec => conv. to seconds
                yield self.irq_thread.flag

        def sleep_example():
            self.scheduler.trace("before")
            with stopwatch:
                yield from sleep(1.3)
            self.scheduler.trace("after: {}".format(stopwatch.elapsed_time))

        self.scheduler.run(sleep_example)
        self.assertRaises(scheduler.ExitScheduler, self.scheduler.run_loop, 2)
        self.assertTrue( 1.299 < stopwatch.elapsed_time < 1.5)


if __name__ == '__main__':
    unittest.main()
