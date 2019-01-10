import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPForbidden, HTTPInternalServerError
from aiohttp_jinja2 import render_template
from aiohttp_session import session_middleware as session_middleware_, get_session
from aiohttp_session.redis_storage import RedisStorage

log = logging.getLogger(__name__)


@web.middleware
async def session_middleware(request, handler):
    """Wrapper to Session Middleware factory.
    """
    # Do the trick, by passing app & handler back to original session
    # middleware factory. Do not forget to await on results here as original
    # session middleware factory is also awaitable.
    app = request.app
    storage = RedisStorage(app['redis'], httponly=False)
    middleware = session_middleware_(storage)
    return await middleware(request, handler)


@web.middleware
async def csrf_middleware(request, handler):
    """Provides csrf"""
    if request.method == "POST":
        session = await get_session(request)
        token = session.pop('_csrf_token', None)
        formdata = await request.post()
        if not token or token != formdata.get('_csrf_token'):
            log.error(
                'Request to %s was aborted because CSRF tokens mismatched',
                request.rel_url
            )
            raise HTTPForbidden()
    return await handler(request)


def error_pages(overrides):
    @web.middleware
    async def middleware(request, handler):
        try:
            response = await handler(request)
            override = overrides.get(response.status)
            if override is None:
                return response
            else:
                return await override(request, response)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override is None:
                raise
            else:
                return await override(request, ex)

    return middleware


async def handle_40x(request, exc):
    response = render_template('errors/40x.jinja2',
                               request,
                               {'error': exc})
    return response


async def handle_50x(request, exc):
    response = render_template('errors/50x.jinja2',
                               request,
                               {'error': exc})
    return response


error_middleware = error_pages({
    x: handle_40x if x < 500 else handle_50x
    for x in range(401, 600)
})
