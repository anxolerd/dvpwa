import sys
import logging

from aiohttp.web import run_app

from sqli.app import init as init_app

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    app = init_app(sys.argv[1:])

    run_app(app,
            host=app['config']['app']['host'],
            port=app['config']['app']['port'])
