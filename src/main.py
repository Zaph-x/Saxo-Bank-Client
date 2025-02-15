from utils.app_config_reader import read_app_config
from saxo_client import SaxoClient
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
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    app_config = read_app_config(args.config)
    saxo_client = SaxoClient(app_config)
    saxo_client.authenticate()

    breakpoint()
