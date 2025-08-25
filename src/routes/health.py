from flask import request
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
from utils.database import Database
import logging

logger = logging.getLogger(__name__)

@inject
def health_check(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Health check endpoint to verify the service is running.
    """

    def handle_GET():
        """
        Handle GET request for health check.
        """
        status_list = []
        logger.debug("Received health check request method: %s", request.method)
        status_list.append(1) if saxo_client.can_trade else status_list.append(0)
        with Database() as db:
            itms = db.execute("SELECT 1")
            status_list.append(1) if itms and len(itms) == 1 else status_list.append(0)


        verdict = all(isinstance(e, int) and e == 1 for e in status_list)
        return {
            "status": "healthy" if verdict else "unhealthy",
            "message": "Service is running." if verdict else "Service is not connected to Saxo.",
            "status_code": 200 if verdict else 503,
        }

    if request.method == "GET":
        return handle_GET()

def ready_check():
    """
    Readiness check endpoint to verify the service is ready to accept requests.
    """

    def handle_GET():
        """
        Handle GET request for readiness check.
        """
        return {
            "status": "ready",
            "message": "Service is ready to accept requests.",
            "status_code": 200,
        }

    if request.method == "GET":
        return handle_GET()
