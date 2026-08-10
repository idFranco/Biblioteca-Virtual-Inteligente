import pytest

from app.schemas import ChatRequest, ChatResponse


def test_chat_request_valid():
    request = ChatRequest(message="¿Tienen Cien años de soledad?", userId="u-1")
    assert request.message == "¿Tienen Cien años de soledad?"
    assert request.userId == "u-1"


def test_chat_request_rejects_empty_message():
    with pytest.raises(Exception):
        ChatRequest(message="", userId=None)


def test_chat_response_with_offer():
    from app.schemas import BookRequestMetadata

    response = ChatResponse(
        message="Solicita una copia",
        action_offer=BookRequestMetadata(title="Cien años de soledad", author="García Márquez"),
        correlation_id="abc",
    )
    assert response.action_offer is not None
    assert response.action_offer.type == "book_request"
