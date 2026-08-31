import socket

import pytest


def qdrant_available() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 6333), timeout=0.4).close()
    except OSError:
        return False
    try:
        from src.qdrant_store import get_client

        get_client().get_collections()
        return True
    except Exception:
        return False


def collection_indexed(name: str = "incident_memory") -> bool:
    if not qdrant_available():
        return False
    try:
        from src.qdrant_store import get_client

        info = get_client().get_collection(name)
        return (info.points_count or 0) > 0
    except Exception:
        return False


@pytest.fixture(scope="session")
def qdrant_up():
    if not qdrant_available():
        pytest.skip("Qdrant not running")
    return True


@pytest.fixture(scope="session")
def indexed_collection(qdrant_up):
    if not collection_indexed():
        pytest.skip("collection not indexed")
    return True


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires Qdrant")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "qdrant_up" in getattr(item, "fixturenames", ()) or "indexed_collection" in getattr(
            item, "fixturenames", ()
        ):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(autouse=True)
def disable_rerank(monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "false")
    from src.settings import reset_settings

    reset_settings()
