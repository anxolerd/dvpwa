from argparse import ArgumentParser

from aiohttp.web import Application
from aiohttp_jinja2 import setup as setup_jinja
from jinja2.loaders import PackageLoader
from trafaret_config import commandline

from sqli.middlewares import session_middleware, error_middleware
from sqli.schema.config import CONFIG_SCHEMA
from sqli.services.db import setup_database
from sqli.services.redis import setup_redis
from sqli.utils.jinja2 import csrf_processor, auth_user_processor
from .routes import setup_routes


def init(argv):
    ap = ArgumentParser()
    commandline.standard_argparse_options(ap, default_config='./config/dev.yaml')
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, CONFIG_SCHEMA)

    app = Application(
        debug=True,
        middlewares=[
            session_middleware,
            # csrf_middleware,
            error_middleware,
        ]
    )
    app['config'] = config

    setup_jinja(app, loader=PackageLoader('sqli', 'templates'),
                context_processors=[csrf_processor, auth_user_processor],
                autoescape=False)
    setup_database(app)
    setup_redis(app)
    setup_routes(app)

    return app
