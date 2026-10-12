import pytest

from src import hevy_client


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_fetch_all_workouts_recorre_todas_las_paginas(monkeypatch):
    pages = {
        1: FakeResponse(200, {"page": 1, "page_count": 2, "workouts": [{"id": "a"}, {"id": "b"}]}),
        2: FakeResponse(200, {"page": 2, "page_count": 2, "workouts": [{"id": "c"}]}),
    }
    calls = []

    def fake_get(url, headers, params, timeout):
        calls.append((url, headers, params))
        return pages[params["page"]]

    monkeypatch.setattr(hevy_client.requests, "get", fake_get)

    workouts = hevy_client.fetch_all_workouts(api_key="test-key", base_url="https://example.com")

    assert [w["id"] for w in workouts] == ["a", "b", "c"]
    assert calls[0][0] == "https://example.com/v1/workouts"
    assert calls[0][1]["api-key"] == "test-key"


def test_fetch_all_workouts_sin_entrenamientos(monkeypatch):
    monkeypatch.setattr(hevy_client.requests, "get", lambda *a, **k: FakeResponse(404))

    assert hevy_client.fetch_all_workouts(api_key="test-key") == []


def test_fetch_all_workouts_sin_api_key():
    with pytest.raises(RuntimeError):
        hevy_client.fetch_all_workouts(api_key="")
