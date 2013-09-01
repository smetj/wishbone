#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  wishbone_actor_tests.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

try:
    from wishbone.tools import WishboneQueue
    from wishbone.errors import QueueFull, QueueEmpty, QueueEmpty, QueueLocked
except:
    pass


class TestWishboneToolsWishboneQueue():

    def test_import(self):
        try:
            from wishbone.tools import WishboneQueue
        except:
            assert WishboneQueue

    def test_init_max_size(self):
        queue = WishboneQueue(max_size=1)
        queue.put("test")
        try:
            queue.put("test")
        except QueueFull:
            pass
        else:
            raise AssertionError("Queue max_size does not appear to be working.")

    def test_clear(self):
        queue = WishboneQueue()
        queue.put("test")
        assert queue.size() == 1

    def test_dump(self):
        queue = WishboneQueue()
        queue.put("test")
        queue.put("test")

        assert len([x for x in queue.dump()]) == 2

    def test_empty(self):
        queue = WishboneQueue()
        queue.put("test")
        queue.clear()
        assert queue.size() == 0

    def test_get(self):
        queue = WishboneQueue()
        queue.put("test")
        assert queue.get() == "test"

    def test_getLock(self):
        queue = WishboneQueue()
        queue.put("test")
        queue.getLock()
        try:
            queue.get()
        except QueueLocked:
            pass
        else:
            raise AssertionError ("Queue getLock does not seem to have the desired effect.")

    def test_getUnlock(self):
        queue = WishboneQueue()
        queue.put("test")
        queue.getLock()
        try:
            queue.get()
        except QueueLocked:
            queue.getUnlock()
            assert queue.get() == "test"
        else:
            raise AssertionError ("Queue getLock() does not seem to have the desired effect.")

    def test_isLocked(self):
        queue = WishboneQueue()
        queue.getLock()
        assert queue.isLocked() == (True, False)

    def test_lock(self):
        queue = WishboneQueue()
        queue.put("test")
        queue.lock()
        try:
            queue.put("test")
        except QueueLocked:
            pass
        else:
            raise AssertionError("Queue lock() not having desired effect.")

        try:
            queue.get()
        except QueueLocked:
            pass
        else:
            raise AssertionError("Queue lock not having desired effect.")

        assert queue.isLocked() == (True, True)

    def test_putLock(self):
        queue = WishboneQueue()
        queue.putLock()

        try:
            queue.put("test")
        except QueueLocked:
            pass
        else:
            raise AssertionError("Queue putLock() not having desired effect.")

    def test_putUnlock(self):
        queue = WishboneQueue()
        queue.putLock()
        try:
            queue.put("test")
        except QueueLocked:
            pass
        else:
            raise AssertionError ("Queue putUnlock() does not seem to have the desired effect.")

    def test_rescue(self):
        queue = WishboneQueue()
        queue.lock()
        queue.rescue("test")
        queue.unlock()
        assert queue.get() == "test"

    def test_size(self):
        queue = WishboneQueue()
        queue.lock()
        queue.rescue("test")
        assert queue.size() == 1


    def test_stats(self):
        queue = WishboneQueue()

        for _ in xrange(10):
            queue.put("test")

        for _ in xrange(9):
            queue.get()

        stats = queue.stats()

        assert isinstance(stats, dict)
        assert stats["in_total"] == 10
        assert stats["out_total"] == 9
        assert stats["size"] == 1


    def test_unlock(self):
        queue = WishboneQueue()
        queue.lock()

        try:
            queue.put("test")
        except QueueLocked:
            queue.unlock()
            try:
                queue.put("test")
            except QueueLocked:
                raise AssertionError("Queue unlock() does not seem to have the desired effect.")
            else:
                pass
        else:
            raise AssertionError ("Queue lock() does not seem to have the desired effect.")

    def test_waitUntilData(self):
        from gevent import spawn, sleep
        def go(queue):
            queue.waitUntilData()

        queue = WishboneQueue()
        queue.put("blah")
        instance=spawn(go, queue)
        sleep()
        assert instance.ready()

        queue = WishboneQueue()
        instance=spawn(go, queue)
        sleep()
        assert not instance.ready()

    def test_waitUntilFreePlace(self):
        from gevent import spawn, sleep
        def go(queue):
            queue.waitUntilFreePlace()

        queue = WishboneQueue(max_size=1)
        queue.put("test")

        instance=spawn(go, queue)
        sleep()
        assert not instance.ready()

        queue.get()
        sleep()
        assert instance.ready()

    def test_waitUntilGetAllowed(self):
        from gevent import spawn, sleep
        def go(queue):
            queue.waitUntilGetAllowed()

        queue = WishboneQueue()
        queue.put("test")
        queue.getLock()

        instance=spawn(go, queue)
        sleep()
        assert not instance.ready()

        queue.getUnlock()
        sleep()
        assert instance.ready()

    def test_waitUntilPutAllowed(self):
        from gevent import spawn, sleep
        def go(queue):
            queue.waitUntilPutAllowed()
            queue.put("test")

        queue = WishboneQueue()
        queue.putLock()

        instance=spawn(go, queue)
        sleep()
        assert not instance.ready()

        queue.putUnlock()
        sleep()
        assert instance.ready()
