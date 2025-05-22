class ClientConfiguration:
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

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
        ClientConfiguration.redis_host = host

    @staticmethod
    def set_redis_port(port: int):
        """
        Set the Redis port.

        Args:
            port (int): The new Redis port.
        """
        ClientConfiguration.redis_port = port

    @staticmethod
    def set_redis_db(db: int):
        """
        Set the Redis database number.

        Args:
            db (int): The new Redis database number.
        """
        ClientConfiguration.redis_db = db

    @staticmethod
    def get_redis_host() -> str:
        """
        Get the Redis host.

        Returns:
            str: The Redis host.
        """
        return ClientConfiguration.redis_host

    @staticmethod
    def get_redis_port() -> int:
        """
        Get the Redis port.

        Returns:
            int: The Redis port.
        """
        return ClientConfiguration.redis_port

    @staticmethod
    def get_redis_db() -> int:
        """
        Get the Redis database number.

        Returns:
            int: The Redis database number.
        """
        return ClientConfiguration.redis_db
