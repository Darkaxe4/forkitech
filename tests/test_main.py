import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from datetime import datetime
from functools import lru_cache

from app.main import app
from app.database import Base, get_db
from app.models import WalletQuery
from app.settings import Settings, get_settings

class TestSettings(Settings):
    database_url: str = "sqlite+aiosqlite:///./test.db"
    tron_network: str = "nile"  # Use testnet for testing

@lru_cache()
def get_test_settings() -> Settings:
    return TestSettings()

# Test database URL from settings
engine = create_async_engine(
    get_test_settings().database_url,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
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
        timestamp=datetime.utcnow()
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
    async with AsyncClient(app=app_client, base_url="http://test") as ac:
        response = await ac.get("/wallet-queries/?page=1&size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert data["page"] == 1
    assert data["size"] == 10

