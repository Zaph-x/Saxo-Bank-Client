from objects.client_configuration import ClientConfiguration
import argparse
import logging
from flask import Flask

logger = logging.getLogger(__name__)

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
        default="redis",
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


def create_app():
    """Create a Flask application."""
    from container import Container
    from urls import register_blueprints
    container = Container()
    container.init_resources()
    container.wire(modules=["routes.trade", "routes.account"])
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
    logging.basicConfig(level=args.loglevel.upper())

    ClientConfiguration.set_redis_host(args.redis_host)
    ClientConfiguration.set_redis_port(args.redis_port)
    ClientConfiguration.set_redis_db(args.redis_db)
    logger.debug("Client configuration set from command line arguments")
    

    if args.interactive:
        from saxo_client import SaxoClient
        from redis import StrictRedis

        client = SaxoClient(
            StrictRedis(
                host=args.redis_host, port=args.redis_port, db=args.redis_db, decode_responses=True, encoding="utf-8"
            )
        )
        breakpoint()

    app = create_app()

    app.run(debug=args.loglevel.upper() == "DEBUG", host="0.0.0.0", port=5000)
