.. _quickstart:

***********
Quick Start
***********

Install aioredlock-py
=======================

Supports python3.7 or later.

- Install from PyPI:

.. code-block:: 

    pip instal aioredlock-py

Basic Usage
===========

When Redisson behaves as a pessimistic lock used in a scenario for inter-process state synchronization, although we do not take a blocking-notification approach, but rather similar to biased locks's trial-and-error manner implement by default.

Here's a basic example:

.. code-block:: python

    import asyncio
    import aioredis
    from aioredlock_py import Redisson

    async def single_thread(redis):
        for _ in range(10):
            async with Redisson(redis, key="no1") as lock:
                if not lock:
                    # If the lock still fails after several attempts, `__aenter__` 
                    # will return None to prompt you to cancel the following execution
                    return 'Do something, failed to acquire lock' # raise ...
                # else 
                # Service logic protected by Redisson
                await redis.incr("foo")

    async def test_long_term_occupancy(redis):
        async with Redisson(redis, key="no1", ex=10) as lock:
            if not lock: return;
            # Service logic protected by Redisson
            await redis.set("foo", 0)
            # By default, a lock is automatically released if no action is 
            # taken for 20 seconds after redisson holds it. Let's assume that 
            # your service logic takes a long time (30s in this case) to process,
            # you don't need to worry about it causing chaos, because there's 
            # background threads help you automatically renew legally held locks.
            await asyncio.sleep(30)
            await redis.incr("foo")


    async def main():
        redis = aioredis.from_url("redis://localhost")
        await redis.delete("redisson:no1")
        await redis.set("foo", 0)
        await asyncio.gather(*(single_thread(redis) for _ in range(20)))
        assert (await redis.get("foo")) == 200
        # test_long_term_occupancy(redis)

    asyncio.run(main())