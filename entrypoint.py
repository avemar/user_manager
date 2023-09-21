import asyncio
import logging

from tornado.platform.asyncio import AsyncIOMainLoop

from application import (
    initialize_application,
    initialize_web_application,
    shutdown_application,
)

logger = logging.getLogger()


def main(io_loop):
    AsyncIOMainLoop().install()
    app_config, _ = io_loop.run_until_complete(initialize_application())
    app = initialize_web_application()
    app.listen(app_config.port)
    try:
        logger.info(f"user_manager running on port {app_config.port}")
        io_loop.run_forever()
    except Exception:
        logger.exception(f"Error encountered while user_manager was running")
    finally:
        io_loop.run_until_complete(shutdown_application())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    main(loop)
