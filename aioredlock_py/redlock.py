import sys
import uuid
import asyncio
from random import random
from typing import Any
from aioredis.client import Redis

if sys.version_info >= (3, 8):
    from typing import Literal
    from asyncio.exceptions import TimeoutError
else:
    from typing_extensions import Literal
    from asyncio import TimeoutError

    
class RedLock:

    _scriper = [None, ]

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._scriper = cls._scriper
        return instance

    def __init__(self, 
        redis: Redis, 
        key: str = 'global', 
        ex: int = 10,              # Automatic expiration time, unit: sec.
        sleeptime_l: float = 0.02, # Default is suitable for short time consuming scenarios, 
        sleeptime_h: float = 0.1,  # such as inter-process state synchronization.
        retry_times: int = 10,
        carry: Any = None,         # Used to carry additional information, may be useful when debugging
    ) -> Literal['RedLock']:
        self.redis = redis
        self._lock_uuid = str(uuid.uuid4())
        self._lock_key = f"redlock:{key}"
        self._ex = ex
        self._sleepattr_k = (sleeptime_h - sleeptime_l)
        self._sleepattr_b = sleeptime_l
        self._sleepattr_avg = (sleeptime_h + sleeptime_l) / 2
        self._get_lock = False
        self._retry_times = retry_times
        self.carry = carry

    def is_locked(self):
        return self._get_lock

    async def __aenter__(self):
        for _ in range(self._retry_times): # CAS
            lock_status = await self.redis.set(self._lock_key, self._lock_uuid, nx=True, ex=self._ex)
            if lock_status:
                self._get_lock = True; break
            # Retry after sleep if no lock is obtained. Sleep time is basically random
            # to avoid hotspot issues. The minimum wait time and maximum wait time 
            # can be set by `sleeptime_l` and `sleeptime_h` respectively when creating
            # the object, who's set default for tasks that take very little time, 
            # if your code to execute after getting the lock requires somewhat longer 
            # time consuming, then maybe you need to increase the time as appropriate 
            # to reduce unnecessary attempts.
            #
            # Based on the frequency distribution of the number of attempts until
            # success, the first three attempts will go very fast, after which each 
            # failure will increase the sleep time until the next attempt.
            await asyncio.sleep(self._sleepattr_avg * max(0, _ - 2) + random.random() * self._sleepattr_k + self._sleepattr_b)
        else:
            return None
            # raise TimeoutError()
        return self
    
    async def __aexit__(self, type, value, trace):
        if self._get_lock:
            script = self._scriper[0]
            if not script:
            	# By default, the first parameter is read using the `KEYS` keyword 
            	# and the second parameter is read using `ARGV` keyword. Here we pass 
            	# a tuple of length 2 to `KEYS`. Use the singleton pattern to avoid 
            	# repeated creation.
                script = self.redis.register_script("if redis.call('get', KEYS[1]) == KEYS[2] then return redis.call('del', KEYS[1]) else return 0 end")
                self._scriper[0] = script
            await script((self._lock_key, self._lock_uuid))
            self._get_lock = False
        return False