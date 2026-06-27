"""Tests for the secret resolver."""

import os
from unittest.mock import patch, MagicMock

from kerygma_profiles.secrets import resolve_secret, clear_cache


class TestResolveSecret:
    def setup_method(self):
        clear_cache()

    def test_literal_passthrough(self):
        assert resolve_secret("plain-text-value") == "plain-text-value"

    def test_empty_string(self):
        assert resolve_secret("") == ""

    def test_none_passthrough(self):
        assert resolve_secret(None) is None

    def test_env_resolution(self):
        with patch.dict(os.environ, {"MY_SECRET_VAR": "secret-value"}):
            assert resolve_secret("env://MY_SECRET_VAR") == "secret-value"

    def test_env_missing_returns_empty(self):
        result = resolve_secret("env://NONEXISTENT_VAR_12345")
        assert result == ""

    def test_op_resolution_success(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "resolved-secret\n"
        with patch("kerygma_profiles.secrets.subprocess.run", return_value=mock_result):
            result = resolve_secret("op://kerygma/mastodon-system/access-token")
            assert result == "resolved-secret"

    def test_op_resolution_cached(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "cached-secret\n"
        with patch("kerygma_profiles.secrets.subprocess.run", return_value=mock_result) as mock_run:
            result1 = resolve_secret("op://kerygma/item/field")
            result2 = resolve_secret("op://kerygma/item/field")
            assert result1 == "cached-secret"
            assert result2 == "cached-secret"
            assert mock_run.call_count == 1  # only called once, second was cached

    def test_op_fallback_to_env(self):
        """When op CLI is not found, falls back to KERYGMA_PROFILE_* env var."""
        with patch(
            "kerygma_profiles.secrets.subprocess.run",
            side_effect=FileNotFoundError("op not found"),
        ):
            with patch.dict(
                os.environ,
                {"KERYGMA_PROFILE_MASTODON_SYSTEM_ACCESS_TOKEN": "env-fallback"},
            ):
                result = resolve_secret("op://kerygma/mastodon-system/access-token")
                assert result == "env-fallback"

    def test_op_fallback_no_env_returns_empty(self):
        """When op CLI fails and no env var, returns empty string."""
        with patch(
            "kerygma_profiles.secrets.subprocess.run",
            side_effect=FileNotFoundError("op not found"),
        ):
            result = resolve_secret("op://kerygma/nonexistent/field")
            assert result == ""

    def test_clear_cache(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "secret\n"
        with patch("kerygma_profiles.secrets.subprocess.run", return_value=mock_result) as mock_run:
            resolve_secret("op://vault/item/field")
            assert mock_run.call_count == 1

            clear_cache()

            resolve_secret("op://vault/item/field")
            assert mock_run.call_count == 2  # called again after cache clear
