from dependency_injector import containers, providers
from objects.client_configuration import ClientConfiguration
from saxo_client import SaxoClient
from redis import StrictRedis


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container for the application."""

    # Redis client
    redis_client = providers.Singleton(
        StrictRedis,
        host=ClientConfiguration.get_redis_host(),
        port=ClientConfiguration.get_redis_port(),
        db=ClientConfiguration.get_redis_db(),
        decode_responses=True,
        encoding="utf-8",
    )

    # Saxo client
    saxo_client = providers.Singleton(
        SaxoClient,
        redis=redis_client,
    )
