import asyncio
import logging
import os
from typing import Tuple

from tornado import web

from application.lib.log.handler import QueueListenerHandler
from application.lib.utils import config
from application.lib.utils.config import DatabaseConfig, ApplicationConfig

from application.datastore.db import get_db_managers
from application.lib.cache import UserExistenceCache
from application.lib.log.formatter import CustomJsonFormatter
from application.lib.tornado.application import WebApplication
from application.controllers.user import (
    UserWriteController,
    UserReadController,
    UserLoginController,
)


logger = logging.getLogger()


def load_configurations() -> Tuple[ApplicationConfig, DatabaseConfig]:
    """Reads and loads config files from default locations"""
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    db_conf_filepath = os.path.join(
        curr_dir, os.environ.get("DB_CONFIG", "../config/database.json")
    )
    app_conf_filepath = os.path.join(
        curr_dir, os.environ.get("APP_CONFIG", "../config/application.json")
    )

    db_config = config.DatabaseConfig(db_conf_filepath)
    app_config = config.ApplicationConfig(app_conf_filepath)

    return app_config, db_config


def init_log(loglevel: str):
    formatter = CustomJsonFormatter("%(levelname)s %(message)s %(asctime)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    queue_handler = QueueListenerHandler([stream_handler])
    logger.addHandler(queue_handler)
    logger.setLevel(level=loglevel)


async def init_db(db_config: DatabaseConfig):
    for db_manager in get_db_managers():
        await db_manager(db_config).init()


async def init_cache(app_config: ApplicationConfig):
    await UserExistenceCache(app_config).init()


async def initialize_application() -> Tuple[ApplicationConfig, DatabaseConfig]:
    app_config, db_config = load_configurations()
    init_log(app_config.loglevel)
    await init_db(db_config)
    await init_cache(app_config)
    return app_config, db_config


def initialize_web_application() -> web.Application:
    return WebApplication(
        [
            (r"/user", UserWriteController),
            (r"/user/(?P<id>[1-9]\d*)", UserWriteController),
            (r"/user/search", UserReadController),
            (r"/user/login", UserLoginController),
        ]
    )


async def shutdown_application() -> None:
    async def close_logger():
        for handler in logger.handlers:
            handler.close()
            if hasattr(handler, "wait_closed"):
                await handler.wait_closed()

    try:
        logger.info("Application is shutting down")
        await asyncio.gather(
            *[db_manager().close() for db_manager in get_db_managers()]
        )

    except Exception as e:
        logger.error(f"Error encountered while application was shutting down: {e}")
    else:
        logger.info("Application shutdown completed")
    finally:
        await close_logger()
