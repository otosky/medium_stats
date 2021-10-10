import lazy_object_proxy
import pytest
import responses

from medium_stats import StatGrabberPublication
from tests.mocks.mock_responses import mock_homepage


@pytest.fixture(autouse=True)
def patch_statgrabber_publication(mocker, monkeypatch, publication_config):
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
        mock_sg = lazy_object_proxy.Proxy(lambda: StatGrabberPublication(**publication_config))
        mocker.patch("medium_stats.cli.publication.sg", mock_sg)
        yield rsps
