import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from datetime import datetime, UTC
from functools import lru_cache
from pydantic import ConfigDict

from app.main import app
from app.database import Base, get_db
from app.models import WalletQuery
from app.settings import Settings, get_settings

@lru_cache()
def get_test_settings() -> Settings:
    return Settings(
        database_url="sqlite+aiosqlite:///./test.db",
        tron_network="nile"  # Use testnet for testing
    )

# Test database URL from settings
engine = create_async_engine(
    get_test_settings().database_url,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        async with TestingSessionLocal() as session:
            yield session
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def override_get_db(test_db):
    async def _override_get_db():
        yield test_db
    return _override_get_db

@pytest.fixture
def override_get_settings():
    return get_test_settings

@pytest.fixture
def app_client(override_get_db, override_get_settings):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    return app

@pytest.mark.asyncio
async def test_create_wallet_query(test_db):
    """Unit test for database writing"""
    wallet_query = WalletQuery(
        wallet_address="TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        trx_balance=100.0,
        bandwidth=1000,
        energy=2000,
        timestamp=datetime.now(UTC)
    )
    
    test_db.add(wallet_query)
    await test_db.commit()
    await test_db.refresh(wallet_query)
    
    query = await test_db.get(WalletQuery, wallet_query.id)
    assert query is not None
    assert query.wallet_address == "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    assert query.trx_balance == 100.0
    assert query.bandwidth == 1000
    assert query.energy == 2000

@pytest.mark.asyncio
async def test_get_wallet_queries(app_client):
    """Integration test for the GET endpoint"""
    expected_page = 1
    expected_size = 10
    
    transport = ASGITransport(app=app_client)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        response = await ac.get(f"/wallet-queries/?page={expected_page}&size={expected_size}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Use more specific assertions
    assert isinstance(data, dict), "Response should be a dictionary"
    required_fields = {"items", "total", "page", "size"}
    assert all(field in data for field in required_fields), f"Missing required fields. Expected: {required_fields}"
    
    assert data["page"] == expected_page, f"Expected page {expected_page}, got {data['page']}"
    assert data["size"] == expected_size, f"Expected size {expected_size}, got {data['size']}"
    
    # Additional validation
    assert isinstance(data["items"], list), "Items should be a list"
    assert isinstance(data["total"], (int, float)), "Total should be a number"




