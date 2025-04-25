from utils.app_config_reader import read_app_config
from data_models.token_data import TokenDataModel
from objects.client_configuration import ClientConfiguration
from saxo_client import SaxoClient
from redis import StrictRedis
import argparse
import logging


def parse_args():
    parser = argparse.ArgumentParser(description="Saxo API Client")
    parser.add_argument("--config", type=str, help="Path to configuration file", default="saxoapp.json")
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
        default=""
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        help="Redis port.",
        default=6379,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    client_config = ClientConfiguration(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        config_file=args.config,
    )
    _state = None
    _token_data = None

    r = StrictRedis(host=args.redis_host, port=args.redis_port, db=0, decode_responses=True, encoding="utf-8")

    if not r.ping():
        logging.error("Could not connect to Redis server. Exiting.")
        exit(1)

    saxo_client = SaxoClient(r, interactive=args.interactive)
    

    user = saxo_client.user

    if saxo_client.interactive:
        breakpoint()
