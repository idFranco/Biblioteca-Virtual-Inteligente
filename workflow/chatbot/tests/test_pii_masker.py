from app.utils.pii_masker import mask_message, mask_pii


def test_mask_email():
    masked = mask_pii("Contacta a admin@biblioteca.com por favor")
    assert "admin@biblioteca.com" not in masked
    assert "[EMAIL]" in masked


def test_mask_phone():
    masked = mask_pii("Mi teléfono es +34 600 123 456")
    assert "[TEL]" in masked


def test_mask_uuid():
    masked = mask_pii("user id 123e4567-e89b-12d3-a456-426614174000 registrado")
    assert "123e4567-e89b-12d3-a456-426614174000" not in masked
    assert "[ID]" in masked


def test_mask_jwt():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    masked = mask_pii(f"el token es {token}")
    assert "[TOKEN]" in masked


def test_mask_location():
    masked = mask_pii("vivo en calle Alcalá 45, Madrid")
    assert "[UBICACIÓN]" in masked


def test_mask_message_replaces_user_id():
    masked = mask_message("hola user-1, recomiéndame algo", "user-1")
    assert "user-1" not in masked
    assert "[USUARIO]" in masked


def test_mask_empty_returns_empty():
    assert mask_pii("") == ""
    assert mask_pii(None) is None
