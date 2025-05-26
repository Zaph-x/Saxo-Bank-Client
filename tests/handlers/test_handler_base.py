import pytest
from unittest.mock import Mock
from requests import Session
from handlers.handler_base import HandlerBase


class TestHandlerBase:
    def test_init_with_valid_session(self):
        """Test initialization with a valid session."""
        session = Mock(spec=Session)
        session.headers = {"Authorization": "Bearer token123"}
        base_url = "https://api.example.com"
        
        handler = HandlerBase(session, base_url)
        
        assert handler.session == session
        assert handler.base_url == base_url
    
    def test_init_with_non_session(self):
        """Test initialization with something that's not a Session."""
        session = "not a session"
        base_url = "https://api.example.com"
        
        with pytest.raises(ValueError, match="session must be a requests.Session"):
            HandlerBase(session, base_url)
    
    def test_init_without_authorization_header(self):
        """Test initialization with a session without Authorization header."""
        session = Mock(spec=Session)
        session.headers = {}
        base_url = "https://api.example.com"
        
        with pytest.raises(ValueError, match="session must have Authorization header"):
            HandlerBase(session, base_url)
    
    def test_init_with_non_string_base_url(self):
        """Test initialization with a non-string base_url."""
        session = Mock(spec=Session)
        session.headers = {"Authorization": "Bearer token123"}
        base_url = 123
        
        with pytest.raises(ValueError, match="base_url must be a string"):
            HandlerBase(session, base_url)
