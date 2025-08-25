from typing import Optional
import humps

class ApiResponse(dict):
    def __init__(self, status_code: int, message: str, **kwargs):
        """
        Initializes an API response object.
        Args:
            status_code (int): HTTP status code for the response.
            message (str): Message describing the response.
            **kwargs: Additional keyword arguments for extra data.
        """
        self.status_code = status_code
        self.message = message
        self.kwargs = kwargs
        self.update(kwargs)
        self["status_code"] = status_code
        self["message"] = message

    def to_dict(self):
        d = {
            "status_code": self.status_code,
            "message": self.message,
        }
        d.update(self.kwargs)
        self.update(d)
        
        return humps.decamelize(d)

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return f"ApiResponse(status_code={self.status_code}, message='{self.message}', kwargs={self.kwargs})"
