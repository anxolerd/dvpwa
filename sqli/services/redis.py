from aiohttp.web import Application
from redis import asyncio as aioredis


def setup_redis(app: Application):
    app.on_startup.append(_init_redis)
    app.on_shutdown.append(_close_redis)


async def _init_redis(app: Application):
    conf = app['config']['redis']
    redis = aioredis.from_url(
        f"redis://{conf['host']}:{conf['port']}/{conf['db']}",
    )
    app['redis'] = redis


async def _close_redis(app: Application):
    app['redis'].close()
