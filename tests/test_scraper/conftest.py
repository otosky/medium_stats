import pytest
import responses

from tests.mocks.mock_responses import mock_homepage


@pytest.fixture()
def responses_fixture():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
        yield rsps
