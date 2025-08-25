import eventlet
eventlet.monkey_patch(all=True)

from dependency_injector.wiring import inject, Provide
from saxo_client import SaxoClient
from container import Container
import argparse
import logging
import os
from flask import Flask
from dotenv import load_dotenv
from utils.database import Database
from streaming.clients import clients
from streaming.upstream import Upstream

load_dotenv()
logger = logging.getLogger(__name__)


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;20m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s|%(name)s|%(levelname)s|%(message)s|%(filename)s:%(lineno)d"

    FORMATS = {
        logging.DEBUG: blue + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def parse_args():
    parser = argparse.ArgumentParser(description="Saxo API Client")
    parser.add_argument(
        "--loglevel",
        type=str,
        help="Logging level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive (debug) mode with breakpoint.",
    )
    parser.add_argument(
        "--redis-host",
        type=str,
        help="Redis host. This overrides the config file setting and will fetch the token data from Redis.",
        default="localhost",
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        help="Redis port.",
        default=6379,
    )
    parser.add_argument(
        "--redis-db",
        type=int,
        help="Redis database number.",
        default=0,
    )
    return parser.parse_args()


@inject
def create_client(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """Create a SaxoClient instance."""
    saxo_client.set_up_handlers()
    return saxo_client

def create_app(args):
    """Create a Flask application."""
    from container import Container
    from urls import register_blueprints
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", args.redis_host)
    container.config.redis_port.from_env("REDIS_PORT", args.redis_port)
    container.config.redis_db.from_env("REDIS_DB", args.redis_db)
    container.wire(modules=["routes.trade", "routes.account", "routes.price", "routes.subscription", __name__])
    logger.debug("Wired container with routes")
    logger.debug(f"Container: {container}")
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.container = container  # pyright: ignore[reportAttributeAccessIssue]

    logger.info("Initialized container resources")
    register_blueprints(app)
    return app


if __name__ == "__main__":
    args = parse_args()
    sh = logging.StreamHandler()
    sh.setFormatter(CustomFormatter())
    logging.basicConfig(level=os.getenv("LOGLEVEL", args.loglevel).upper(), handlers=[sh])
    Database.setup()
    
    if args.interactive:
        from saxo_client import SaxoClient
        from redis import StrictRedis

        client = SaxoClient(
            StrictRedis(
                host=args.redis_host, port=args.redis_port, db=args.redis_db, decode_responses=True, encoding="utf-8"
            )
        )
        breakpoint()

    app = create_app(args)

    client = create_client()
    app.run(debug=args.loglevel.upper() == "DEBUG", use_reloader=False, host="0.0.0.0", port=5000)
