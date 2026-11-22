import io
import os
import random

import numpy as np
import pytest
from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # flip.py loads source.png from cwd
import flip  # noqa: E402


def encode(fmt="PNG", **kw):
    buf = io.BytesIO()
    Image.fromarray(flip.REF.astype(np.uint8)).save(buf, fmt, **kw)
    return buf.getvalue()


@pytest.fixture(scope="module")
def png():
    return encode("PNG")


def test_decode_valid_image_matches_reference(png):
    out = flip.decode(png)
    assert isinstance(out, np.ndarray)
    assert out.shape == flip.REF.shape
    assert np.array_equal(out, flip.REF)


@pytest.mark.parametrize("raw", [b"", b"not an image", b"\x89PNG\r\n\x1a\n" + b"\0" * 8])
def test_decode_garbage_returns_exception_name(raw):
    out = flip.decode(raw)
    assert isinstance(out, str) and out


def test_decode_truncated_image_is_dead(png):
    assert isinstance(flip.decode(png[: len(png) // 2]), str)


def test_trial_is_deterministic_for_same_seed(png):
    assert flip.trial(png, random.Random(1)) == flip.trial(png, random.Random(1))


def test_trial_does_not_mutate_input(png):
    before = bytes(png)
    flip.trial(png, random.Random(2))
    assert png == before


def test_trial_result_shape(png):
    for seed in range(30):
        kind, pct, err, pos = flip.trial(png, random.Random(seed))
        assert kind in {"dead", "wrong size", "identical", "changed"}
        assert 0.0 <= pct <= 100.0
        assert 0.0 <= pos < 1.0
        assert (kind == "dead") == bool(err)
        if kind == "identical":
            assert pct == 0.0


def test_trial_flips_exactly_one_bit(png, monkeypatch):
    seen = []
    monkeypatch.setattr(flip, "decode", lambda raw: seen.append(raw) or "X")
    flip.trial(png, random.Random(3))
    flipped = seen[0]
    assert len(flipped) == len(png)
    assert sum(bin(a ^ b).count("1") for a, b in zip(png, flipped)) == 1


def test_trial_reports_dead_when_decoder_fails(monkeypatch, png):
    monkeypatch.setattr(flip, "decode", lambda raw: "OSError")
    kind, pct, err, _ = flip.trial(png, random.Random(0))
    assert (kind, pct, err) == ("dead", 0.0, "OSError")


def test_trial_wrong_size(monkeypatch, png):
    monkeypatch.setattr(flip, "decode", lambda raw: np.zeros((1, 1, 3), np.int16))
    kind, pct, _, _ = flip.trial(png, random.Random(0))
    assert (kind, pct) == ("wrong size", 100.0)


def test_trial_identical_and_changed(monkeypatch, png):
    monkeypatch.setattr(flip, "decode", lambda raw: flip.REF.copy())
    assert flip.trial(png, random.Random(0))[:2] == ("identical", 0.0)

    damaged = flip.REF.copy()
    damaged[0, 0] += 50
    monkeypatch.setattr(flip, "decode", lambda raw: damaged)
    kind, pct, _, _ = flip.trial(png, random.Random(0))
    assert kind == "changed"
    assert pct == pytest.approx(100 / flip.REF[..., 0].size)
