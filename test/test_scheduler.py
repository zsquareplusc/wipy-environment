#! /usr/bin/env python3
"""\
Tests for task scheduler.
"""

import os
import sys
import traceback
import unittest

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../device/flash/lib'))
import scheduler

sys.print_exception = lambda e: traceback.print_tb(e.__traceback__) or print(e)


class TestScheduler(scheduler.Scheduler):
    def sleep(self):
        print("sleep")


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


if __name__ == '__main__':
    unittest.main()
