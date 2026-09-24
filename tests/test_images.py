import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "SRC", Image.new("RGB", (2, 2), "red"))
    with TestClient(main.app) as client:
        yield client


@pytest.mark.parametrize("fmt", sorted(main.FORMATS))
def test_encode_and_zero_flips(client, fmt):
    raw, mime = main.encode(fmt)
    with Image.open(io.BytesIO(raw)) as image:
        assert image.size == (2, 2)
        assert image.format == main.FORMATS[fmt][0]
    response = client.get("/img", params={"fmt": fmt, "bits": 0})
    assert response.status_code == 200
    assert response.content == raw
    assert response.headers["content-type"] == mime
    assert response.headers["x-bytes"] == str(len(raw))
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("fmt", sorted(main.FORMATS))
@pytest.mark.parametrize("bits", [1, 7, "all"])
def test_exact_number_of_distinct_bits_and_repeatable_seed(client, fmt, bits):
    raw, _ = main.encode(fmt)
    count = len(raw) * 8 if bits == "all" else bits
    params = {"fmt": fmt, "bits": count, "seed": 42}
    first = client.get("/img", params=params)
    second = client.get("/img", params=params)
    assert first.status_code == second.status_code == 200
    assert len(first.content) == len(raw)
    assert sum((a ^ b).bit_count() for a, b in zip(raw, first.content)) == count
    assert first.content == second.content


@pytest.mark.parametrize("fmt", ["unknown", "webp"])
def test_unsupported_format_returns_400(client, monkeypatch, fmt):
    monkeypatch.delitem(main.FORMATS, fmt, raising=False)
    response = client.get("/img", params={"fmt": fmt})
    assert response.status_code == 400
    assert "format" in response.json()["detail"].lower()


def test_too_many_bits_returns_400(client):
    raw, _ = main.encode("png")
    response = client.get("/img", params={"bits": len(raw) * 8 + 1})
    assert response.status_code == 400
