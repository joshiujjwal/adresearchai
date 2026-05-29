"""
Smoke test: Settings loads correctly from environment variables.
This is the Phase 0 gate — run this before any other development.
"""
from __future__ import annotations

import pytest

from src.core.config import Settings, get_settings


def make_env(overrides: dict | None = None) -> dict:
    base = {
        "OPENAI_API_KEY": "sk-test-aaabbbccc",
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "a" * 32,
        "ENV": "test",
    }
    if overrides:
        base.update(overrides)
    return base


def test_settings_load_from_env(monkeypatch):
    env = make_env()
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()
    s = get_settings()
    assert s.openai_api_key == "sk-test-aaabbbccc"
    assert s.env == "test"
    assert s.is_test is True
    assert s.is_production is False


def test_settings_default_values(monkeypatch):
    for k, v in make_env().items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()
    s = get_settings()
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_expire_hours == 24
    assert s.api_prefix == "/api/v1"


def test_secret_key_too_short_raises(monkeypatch):
    env = make_env({"SECRET_KEY": "short"})
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()
    with pytest.raises(Exception):
        get_settings()


def test_missing_openai_key_raises(monkeypatch):
    env = make_env()
    env.pop("OPENAI_API_KEY")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(Exception):
        get_settings()
