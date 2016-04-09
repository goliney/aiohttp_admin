import asyncio
import logging
import pathlib

from aiohttp import web

import aiohttp_admin
from aiohttp_admin.backends.mongo import MotorResource

from minitwit import db
from minitwit.utils import load_config, init_mongo


PROJ_ROOT = pathlib.Path(__file__).parent.parent
TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'templates'


def setup_admin(app, mongo, admin_config_path):
    admin = aiohttp_admin.setup(app, admin_config_path)

    admin.add_resource(MotorResource(
        mongo.user, db.user_schema, url='user'))
    admin.add_resource(MotorResource(
        mongo.message, db.message_schema, url='message'))
    admin.add_resource(MotorResource(
        mongo.follower, db.follower_schema, url='follower'))
    return admin


async def init(loop):
    # setup application and extensions
    app = web.Application(loop=loop)

    # load config from yaml file
    conf = load_config(str(PROJ_ROOT / 'config' / 'dev.yaml'))

    # create connection to the database
    mongo = await init_mongo(conf['mongodb'], loop)

    async def close_mongo(app):
        mongo.close()

    # setup admin views
    admin_config = str(PROJ_ROOT / 'static' / 'js')
    setup_admin(app, mongo, admin_config)

    app.on_cleanup.append(close_mongo)

    # setup views and routes
    # handler = SiteHandler(pg)
    # setup_routes(app, handler, PROJ_ROOT)

    host, port = conf['host'], conf['port']
    return app, host, port


def main():
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
