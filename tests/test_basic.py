import os , sys
sys.path.append(os.getcwd())
import pytest
import aioredis
import asyncio
from aioredlock_py import *

@pytest.mark.asyncio
async def test_basic():
    
    async def single_thread(redis, fail_count):
        for _ in range(10):
            async with RedLock(redis, key="no1") as lock:
                if lock:
                    await redis.incr("foo")
                else:
                    fail_count[0] += 1
                    
    redis = aioredis.from_url("redis://127.0.0.1")
    await redis.set("foo", 0)
    fail_count = [0]
    await asyncio.gather(*(single_thread(redis, fail_count) for _ in range(20)))
    assert int(await redis.get("foo")) == (200 - fail_count[0])
    
