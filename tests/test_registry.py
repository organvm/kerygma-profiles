"""Tests for the profile registry."""

import pytest

from kerygma_profiles.registry import ProfileRegistry


class TestProfileRegistry:
    def test_load_directory(self, tmp_profiles):
        registry = ProfileRegistry()
        count = registry.load_directory(tmp_profiles)
        assert count == 2

    def test_load_nonexistent_directory(self, tmp_path):
        registry = ProfileRegistry()
        count = registry.load_directory(tmp_path / "nonexistent")
        assert count == 0

    def test_list_profiles(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profiles = registry.list_profiles()
        assert len(profiles) == 2
        ids = {p.profile_id for p in profiles}
        assert "_default" in ids
        assert "my-product" in ids

    def test_get_profile(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.get("_default")
        assert profile is not None
        assert profile.display_name == "System Default"

    def test_get_missing_profile(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        assert registry.get("nonexistent") is None

    def test_resolve_by_repo_name(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.resolve("my-product-repo")
        assert profile.profile_id == "my-product"

    def test_resolve_fallback_to_default(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.resolve("unknown-repo")
        assert profile.profile_id == "_default"

    def test_resolve_no_default_raises(self, tmp_path):
        """Resolve raises KeyError when no _default and no match."""
        profiles = tmp_path / "profiles"
        profiles.mkdir()
        (profiles / "specific.yaml").write_text(
            "profile_id: specific\n"
            "display_name: Specific\n"
            "repos:\n"
            "  - specific-repo\n"
            "platforms: {}\n"
            "channels: []\n"
        )
        registry = ProfileRegistry()
        registry.load_directory(profiles)
        with pytest.raises(KeyError, match="no _default"):
            registry.resolve("unmatched-repo")

    def test_total_profiles(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        assert registry.total_profiles == 2

    def test_profile_voice(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.get("my-product")
        assert profile.voice["tone"] == "friendly"
        assert "#myproduct" in profile.voice["hashtags"]

    def test_profile_platforms(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.get("_default")
        assert "mastodon" in profile.platforms
        assert profile.platforms["mastodon"]["instance_url"] == "https://mastodon.social"

    def test_profile_channels(self, tmp_profiles):
        registry = ProfileRegistry()
        registry.load_directory(tmp_profiles)
        profile = registry.get("_default")
        assert len(profile.channels) == 1
        assert profile.channels[0]["channel_id"] == "mastodon-primary"

    def test_invalid_yaml_skipped(self, tmp_path):
        profiles = tmp_path / "profiles"
        profiles.mkdir()
        (profiles / "bad.yaml").write_text("not: a: valid: yaml: [")
        (profiles / "no-id.yaml").write_text("display_name: No ID\n")
        registry = ProfileRegistry()
        count = registry.load_directory(profiles)
        assert count == 0

    def test_load_real_default_profile(self, profiles_dir):
        """Verify the shipped _default.yaml loads correctly."""
        registry = ProfileRegistry()
        count = registry.load_directory(profiles_dir)
        assert count >= 1
        default = registry.get("_default")
        assert default is not None
        assert default.display_name == "ORGANVM System"
