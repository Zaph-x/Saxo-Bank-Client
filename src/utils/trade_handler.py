from requests import Session


class TradeHandler:
    def __init__(self, session: Session):
        if 'Authorization' not in session.headers:
            raise ValueError('No authorization token found in session')
        self.session = session


