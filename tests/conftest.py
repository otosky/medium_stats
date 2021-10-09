import pytest


@pytest.fixture
def config():
    return {
        "uid": "abc123",
        "sid": "xyz456",
    }


@pytest.fixture
def user_config(config):
    return {**config, "username": "foolicious"}


@pytest.fixture
def publication_config(config):
    return {**config, "slug": "foo-blog"}
