import logging

logger = logging.getLogger(__name__)

class ClientConfiguration:
    def __init__(self, redis_host: str, redis_port: int, redis_db: int = 0):
        """
        Initialize the ClientConfiguration with Redis settings.

        Args:
            redis_host (str): The host of the Redis server.
            redis_port (int): The port of the Redis server.
            redis_db (int): The database number to use with Redis. Default is 0.
        """
        ClientConfiguration.set_redis_host(redis_host)
        ClientConfiguration.set_redis_port(redis_port)
        ClientConfiguration.set_redis_db(redis_db)

    @staticmethod
    def set_redis_host(host: str):
        """
        Set the Redis host.

        Args:
            host (str): The new Redis host.
        """
        logger.debug(f"Setting Redis host to {host}")
        ClientConfiguration.redis_host = host

    @staticmethod
    def set_redis_port(port: int):
        """
        Set the Redis port.

        Args:
            port (int): The new Redis port.
        """
        logger.debug(f"Setting Redis port to {port}")
        ClientConfiguration.redis_port = port

    @staticmethod
    def set_redis_db(db: int):
        """
        Set the Redis database number.

        Args:
            db (int): The new Redis database number.
        """
        logger.debug(f"Setting Redis database to {db}")
        ClientConfiguration.redis_db = db

    @staticmethod
    def get_redis_host() -> str:
        """
        Get the Redis host.

        Returns:
            str: The Redis host.
        """
        logger.debug(f"Redis host: {ClientConfiguration.redis_host}")
        return ClientConfiguration.redis_host

    @staticmethod
    def get_redis_port() -> int:
        """
        Get the Redis port.

        Returns:
            int: The Redis port.
        """
        logger.debug(f"Redis port: {ClientConfiguration.redis_port}")
        return ClientConfiguration.redis_port

    @staticmethod
    def get_redis_db() -> int:
        """
        Get the Redis database number.

        Returns:
            int: The Redis database number.
        """
        logger.debug(f"Redis database: {ClientConfiguration.redis_db}")
        return ClientConfiguration.redis_db

    def __repr__(self):
        """
        Return a string representation of the ClientConfiguration.

        Returns:
            str: A string representation of the ClientConfiguration.
        """
        return f"ClientConfiguration(redis_host={self.redis_host}, redis_port={self.redis_port}, redis_db={self.redis_db})"
