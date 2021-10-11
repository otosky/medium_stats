import lazy_object_proxy
import pytest
import responses

# from medium_stats import StatGrabberPublication
from medium_stats import StatGrabberUser
from medium_stats.config import PublicationConfig
from medium_stats.config import UserConfig
from tests.mocks.mock_responses import mock_homepage


@pytest.fixture(autouse=True)
def patch_statgrabber_publication(mocker, publication_config):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
        mock_config = lazy_object_proxy.Proxy(lambda: PublicationConfig(**publication_config))
        mocker.patch("medium_stats.cli.publication.publication_config", mock_config)
        yield


@pytest.fixture(autouse=True)
def patch_statgrabber_user(mocker, user_config):
    mock_config = lazy_object_proxy.Proxy(lambda: UserConfig(**user_config))
    mocker.patch("medium_stats.cli.user.user_config", mock_config)
    yield
