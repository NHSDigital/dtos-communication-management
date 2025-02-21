import app.utils.uuid_generator as uuid_generator
import uuid


def test_reference_uuid():
    """Tests the predictable conversion of a value to a UUID."""
    val = "test"
    assert uuid_generator.reference_uuid(val) == "098f6bcd-4621-d373-cade-4e832627b4f6"


def test_uuid4_str(monkeypatch):
    """Tests the generation of a UUID4 string."""
    monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID("c1a8b6c8-9f6b-4e1e-9d3f-3e7f4b8c0a9d"))
    assert uuid_generator.uuid4_str() == "c1a8b6c8-9f6b-4e1e-9d3f-3e7f4b8c0a9d"
