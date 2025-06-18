#!/usr/bin/env python3

import asyncio
from bernard.storage.register import RedisRegisterStore
from bernard.conf import settings
from dev_provider import video

async def clear_redis():
    """
    Clears the redis database
    """

    store = RedisRegisterStore(**settings.REGISTER_STORE['params'])
    await store.async_init()
    await store.redis.flushdb(True)
    await store.redis.aclose()

def setup():
    """
    Initialization script
    """

    asyncio.run(clear_redis())
    video.setup_frame_endpoint()

if __name__ == "__main__":
    asyncio.run(clear_redis())
    print("Redis ready")
