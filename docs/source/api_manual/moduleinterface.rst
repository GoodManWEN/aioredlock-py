.. module:: aioredlock-py

.. _moduleinterface:

****************
Module Interface
****************

.. function:: __init__(self, redis: aioredis.client.Redis, \
    key: str = 'global', \
    ex: int = 10, \
    sleeptime_l: float = 0.02, \
    sleeptime_h: float = 0.1, \
    retry_count: int = 10, \
    carry: Any = None)

    key: str, use different strings to identify different locks, instances using the same `key` compete for the same lock.

    ex: int, Automatic expiration time, unit: sec.

    sleeptime_l: float = 0.02, the minimum value of random sleep time in case no lock is obtained.

    sleeptime_h: float = 0.1, the maximum value of random sleep time in case no lock is obtained.

    retry_times: int = 10, maximum retry times in case of no lock gained, exceeds which the act of acquiring a lock will be aborted.

    carry: Any = None, used to carry additional information, may be useful when debugging.

    .. note::

        TIPS1: Sleep time is basically randomto avoid hotspot issues. The minimum wait time and maximum wait time can be set by `sleeptime_l` and `sleeptime_h` respectively when creating the object, which is set default for tasks that take very little time, if your code to execute after getting the lock requires some what longer time consuming, then maybe you need to increase the time as appropriate to reduce unnecessary attempts.
        
        Based on the frequency distribution of the number of attempts until success, the first three attempts will go very fast, after which each failure will increase the sleep time until the next attempt.

        TIPS2: There's a background tasks that automatically renew the expire time of redis's lock-key when user's service logic takes longer than the default lock release time to avoid being occupied by other threads. Do make sure that your custom code does not have any actions that will cause the event loop to block. All IO/computing tasks that potentially lead to blocking should be circumvented with a corresponding solution.

    .. versionadded:: 0.1.0

.. function:: is_locked(self) -> bool
    
    Check if the lock is currently engaged by the instance itself.
	
    .. versionadded:: 0.1.0