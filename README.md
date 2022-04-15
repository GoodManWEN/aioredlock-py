# aioredlock-py
[![fury](https://img.shields.io/pypi/v/aioredlock-py.svg)](https://pypi.org/project/aioredlock-py/)
[![licence](https://img.shields.io/github/license/GoodManWEN/aioredlock-py)](https://github.com/GoodManWEN/aioredlock-py/blob/master/LICENSE)
[![pyversions](https://img.shields.io/pypi/pyversions/aioredlock-py.svg)](https://pypi.org/project/aioredlock-py/)
[![Publish](https://github.com/GoodManWEN/aioredlock-py/workflows/Publish/badge.svg)](https://github.com/GoodManWEN/aioredlock-py/actions?query=workflow:Publish)
[![Build](https://github.com/GoodManWEN/aioredlock-py/workflows/Build/badge.svg)](https://github.com/GoodManWEN/aioredlock-py/actions?query=workflow:Build)
[![Docs](https://readthedocs.org/projects/aioredlock-py/badge/?version=latest)](https://readthedocs.org/projects/aioredlock-py/)

Secure and efficient distributed locks implemetation.

## Requirements
- aioredis>=2.0.0

## Install

    pip install aioredlock-py

## Feature
- Ensure reliability with context manager.
- Use lua scripts to ensure atomicity on lock release.
- Notification prompt you to cancel the following execution if acquisition fails
- Reliable in high concurrency.

## Documentation
https://aioredlock-py.readthedocs.io

## Example

Some description.
```python
import asyncio
import aioredis
from aioredlock_py import RedLock

async def single_thread():
    for _ in range(10):
        async with RedLock(redis, key="no1") as lock:
            if lock:
                # Protected service logic
                await redis.incr("foo")
            else:
                # If the lock still fails after several attempts, `__aenter__` 
                # will return None to prompt you to cancel the following execution
                print("Call failure")
                # raise ...

async def main():
    redis = aioredis.from_url("redis://localhost")
    await redis.delete("redlock:no1")
    await redis.set("foo", 0)
    await asyncio.gather(*(thread(redis) for _ in range(20)))
    assert (await redis.get("foo")) == 200

asyncio.run(main())
```

A test of new branch
