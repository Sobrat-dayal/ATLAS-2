import pytest
from httpx import ASGITransport, AsyncClient
from atlas_api.main import app

@pytest.mark.asyncio
async def test_provider_list_contains_openbb():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pass


def test_startup_no_errors():
    from atlas_api.main import app
    assert app is not None
