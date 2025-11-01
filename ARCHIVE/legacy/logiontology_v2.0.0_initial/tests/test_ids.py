from src.core.ids import deterministic_id


def test_deterministic_id_stable():
    a = deterministic_id("transport_event", "SHIP-1", occurred_at="2024-01-01T00:00Z")
    b = deterministic_id("transport_event", "SHIP-1", occurred_at="2024-01-01T00:00Z")
    assert a == b
