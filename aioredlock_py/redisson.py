import sys
import uuid
import asyncio
from random import random
from typing import Any, Optional
from aioredis.client import Redis
# from asyncio import TimeoutError

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
    

    
class Redisson:

    _scriper = [None, None]

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._scriper = cls._scriper
        return instance

    def __init__(self, 
        redis: Redis, 
        key: str = 'global', 
        ex: int = 20,              # Automatic expiration time, unit: sec.
        sleeptime_l: float = 0.02, # Default is suitable for short time consuming scenarios, 
        sleeptime_h: float = 0.1,  # such as inter-process state synchronization.
        retry_times: int = 10,
        carry: Any = None,         # Used to carry additional information, may be useful when debugging
    ) -> Literal['Redisson']:
        self.redis = redis
        self._lock_uuid = str(uuid.uuid4())
        self._lock_key = f"redisson:{key}"
        self._ex = ex
        self._sleepattr_k = (sleeptime_h - sleeptime_l)
        self._sleepattr_b = sleeptime_l
        self._sleepattr_avg = (sleeptime_h + sleeptime_l) / 2
        self._get_lock = False
        self._retry_times = retry_times
        self._daemon_extend_interval = ex * 0.667
        self._close_triggered = False
        self._daemon_task = None
        self.carry = carry

    def is_locked(self):
        return self._get_lock

    async def __aenter__(self) -> Optional['Redisson']:
        for _ in range(self._retry_times): # CAS
            lock_status = await self.redis.set(self._lock_key, self._lock_uuid, nx=True, ex=self._ex)
            if lock_status:
                self._get_lock = True
                loop = asyncio.get_running_loop()
                self._daemon_task = loop.create_task(self._daemon_thread())
                break
            # Retry after sleep if no lock is obtained. Sleep time is basically random
            # to avoid hotspot issues. The minimum wait time and maximum wait time 
            # can be set by `sleeptime_l` and `sleeptime_h` respectively when creating
            # the object, which is set default for tasks that take very little time, 
            # if your code to execute after getting the lock requires somewhat longer 
            # time consuming, then maybe you need to increase the time as appropriate 
            # to reduce unnecessary attempts.
            #
            # Based on the frequency distribution of the number of attempts until
            # success, the first three attempts will go very fast, after which each 
            # failure will increase the sleep time until the next attempt.
            await asyncio.sleep(self._sleepattr_avg * max(0, _ - 2) + random() * self._sleepattr_k + self._sleepattr_b)
        else:
            return None
            # raise TimeoutError()
        return self
    
    async def __aexit__(self, type, value, trace):
        self._close_triggered = True
        if self._daemon_task:
            self._daemon_task.cancel()
        if self._get_lock:
            script0 = self._scriper[0]
            if not script0:
            	# By default, the first parameter is read using the `KEYS` keyword 
            	# and the second parameter is read using `ARGV` keyword. Here we pass 
            	# a tuple of length 2 to `KEYS`. Use the singleton pattern to avoid 
            	# repeated creation.
                script0 = self.redis.register_script("if redis.call('get', KEYS[1]) == KEYS[2] then return redis.call('del', KEYS[1]) else return 0 end")
                self._scriper[0] = script0
            await script0((self._lock_key, self._lock_uuid))
            self._get_lock = False
        return False

    async def _daemon_thread(self):
        # Background tasks that automatically renew contract when 
        # user's service logic takes longer than the default lock 
        # release time to avoid being occupied by other threads.
        while True:
            await asyncio.sleep(self.self._daemon_extend_interval)
            if self._close_triggered:
                # To deal with special cases where lock release has not 
                # occurred, ensure that the thread will certainly end 
                # when the context manager is released.
                break
            if self._get_lock:
                script1 = self._scriper[1]
                if not script1:
                    script1 = self.redis.register_script("if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('expire', KEYS[1], ARGV[2]) else return 0 end")
                    self._scriper[1] = script1
                await script1((self._lock_key, ), (self._lock_uid, self._ex))
