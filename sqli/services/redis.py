import aioredis
from aiohttp.web import Application


def setup_redis(app: Application):
    app.on_startup.append(_init_redis)
    app.on_shutdown.append(_close_redis)


async def _init_redis(app: Application):
    conf = app['config']['redis']
    redis = await aioredis.create_pool((conf['host'], conf['port']),
                                       db=conf['db'])
    app['redis'] = redis


async def _close_redis(app: Application):
    app['redis'].close()
    await app['redis'].wait_closed()
