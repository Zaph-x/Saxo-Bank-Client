from requests import Session


class HandlerBase:
    base_url: str

    def __init__(self, session: Session, base_url: str) -> None:
        if not isinstance(session, Session):
            raise ValueError("session must be a requests.Session")
        if not "Authorization" in session.headers:
            raise ValueError("session must have Authorization header")
        if not isinstance(base_url, str):
            raise ValueError("base_url must be a string")

        self.base_url = base_url
        self.session = session
