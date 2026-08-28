import pytest

from app.schemas import ChatRequest, ChatResponse


def test_chat_request_valid():
    request = ChatRequest(message="¿Tienen Cien años de soledad?", userId="u-1")
    assert request.message == "¿Tienen Cien años de soledad?"
    assert request.userId == "u-1"


def test_chat_request_accepts_conversation_id():
    request = ChatRequest(message="hola", userId="u-1", conversationId="conv-abc")
    assert request.conversationId == "conv-abc"


def test_chat_response_accepts_conversation_id():
    response = ChatResponse(message="hola", conversation_id="conv-abc")
    assert response.conversation_id == "conv-abc"


def test_book_recommendation_source_and_verified():
    from app.schemas import BookRecommendation

    rec = BookRecommendation(
        title="Rayuela",
        source="open_library",
        openLibraryVerified=True,
        availableCopies=0,
    )
    assert rec.source == "open_library"
    assert rec.openLibraryVerified is True


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
