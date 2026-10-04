import pytest
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.config import get_settings


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def settings():
    return get_settings()


@pytest.mark.asyncio
async def test_health_endpoint(app, settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(f"{settings.api_prefix}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == settings.app_name


@pytest.mark.asyncio
async def test_ready_endpoint(app, settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(f"{settings.api_prefix}/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_version_endpoint(app, settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(f"{settings.api_prefix}/system/version")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == settings.app_name
        assert data["environment"] == settings.env.value


@pytest.mark.asyncio
async def test_not_found_handling(app, settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(f"{settings.api_prefix}/does-not-exist")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_request_id_in_header(app, settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(f"{settings.api_prefix}/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # Test custom ID
        response2 = await client.get(f"{settings.api_prefix}/health", headers={"X-Request-ID": "custom-id-123"})
        assert response2.status_code == 200
        assert response2.headers["X-Request-ID"] == "custom-id-123"


@pytest.mark.asyncio
async def test_openapi_json(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
