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

When RedLock behaves as a pessimistic lock used in a scenario for inter-process state synchronization, although we do not take a blocking-notification approach, but rather similar to biased locks's trial-and-error manner implement by default.

Here's a basic example:

.. code-block:: python

    import asyncio
    import aioredis
    from aioredlock_py import RedLock
    
    async def single_thread(redis):
        for _ in range(10):
            async with RedLock(redis, key="no1") as lock:
                if lock:
                    # Protected service logic
                    await redis.incr("foo")
                else:
                    # If the lock still fails after several attempts, `__aenter__` 
                    # will return None to prompt you to cancel the following execution
                    print("Call failure")

    async def main():
        redis = aioredis.from_url("redis://localhost")
        await redis.delete("redlock:no1")
        await redis.set("foo", 0)
        await asyncio.gather(*(single_thread(redis) for _ in range(20)))
        assert (await redis.get("foo")) == 200
    
    asyncio.run(main())