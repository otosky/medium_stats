import pytest

from medium_stats.config import PublicationConfig
from medium_stats.config import UserConfig
from medium_stats.config import get_env_var_or_raise


class TestEnvVarOrRaise:
    def test_when_set(self, monkeypatch):
        monkeypatch.setenv("FOO", "a")
        assert get_env_var_or_raise("FOO") == "a"

    def test_raises_key_error(self):
        with pytest.raises(KeyError):
            get_env_var_or_raise("FOO")


class TestPublicationConfig:
    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("MEDIUM_SID", "a")
        monkeypatch.setenv("MEDIUM_UID", "b")
        monkeypatch.setenv("MEDIUM_PUBLICATION_SLUG", "c-d-e")
        config = PublicationConfig.from_env()

        assert config.sid == "a"
        assert config.uid == "b"
        assert config.slug == "c-d-e"

    def test_as_dict(self):
        as_dict = PublicationConfig(sid="a", uid="b", slug="c-d-e").as_dict()
        assert as_dict == {"sid": "a", "uid": "b", "slug": "c-d-e"}

    def test_cli_config_singletons(self, monkeypatch):
        monkeypatch.setenv("MEDIUM_SID", "a")
        monkeypatch.setenv("MEDIUM_UID", "b")
        monkeypatch.setenv("MEDIUM_PUBLICATION_SLUG", "c-d-e")
        from medium_stats.config import publication_config

        assert publication_config.sid == "a"
        assert publication_config.uid == "b"
        assert publication_config.slug == "c-d-e"


class TestUserConfig:
    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("MEDIUM_SID", "a")
        monkeypatch.setenv("MEDIUM_UID", "b")
        monkeypatch.setenv("MEDIUM_USERNAME", "foobar")
        config = UserConfig.from_env()

        assert config.sid == "a"
        assert config.uid == "b"
        assert config.username == "foobar"

    def test_as_dict(self):
        as_dict = UserConfig(sid="a", uid="b", username="foobar").as_dict()
        assert as_dict == {"sid": "a", "uid": "b", "username": "foobar"}

    def test_cli_config_singletons(self, monkeypatch):
        monkeypatch.setenv("MEDIUM_SID", "a")
        monkeypatch.setenv("MEDIUM_UID", "b")
        monkeypatch.setenv("MEDIUM_USERNAME", "foobar")
        from medium_stats.config import user_config

        assert user_config.sid == "a"
        assert user_config.uid == "b"
        assert user_config.username == "foobar"
